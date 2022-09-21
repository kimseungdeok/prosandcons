import hashlib
from flask import Flask, render_template, request, jsonify, make_response, redirect, flash, url_for
import mongo_connetion
from s3_connection import s3_connection
from config import *
from werkzeug.utils import secure_filename
import datetime
import uuid
from flask_jwt_extended import *
import os

import config
import dto

app = Flask(__name__)
app.secret_key = 'some_secret'
app.config.update(
    DEBUG=True,
    JWT_SECRET_KEY=config.JWT_SECRET_KEY
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=12)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

db = mongo_connetion.get_mongo_connection()
jwt = JWTManager(app)


@app.route('/', methods=['GET'])
def get_main_page():
    now = datetime.datetime.now()
    return render_template('signin.j2', current_time=now)


@app.route('/login', methods=['POST'])
def login():
    id = request.form['id']
    pw = request.form['pw']
    encoded_pw = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    pw_from_db = ""
    for x in db.users.find({"id": id}, {"pw": 1}):
        pw_from_db = x['pw']
    if len(pw_from_db) == 0:
        return make_response("존재하지 않는 유저입니다.", 400)
    if encoded_pw == pw_from_db:
        # 여기에 JWT or 쿠키 추가
        response = make_response(redirect("/users"))
        access_token = create_access_token(identity=id)
        set_access_cookies(response, access_token)
        return response
    return make_response("비밀번호가 일치하지 않습니다.", 400)


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.datetime.now(datetime.timezone.utc)
        target = datetime.datetime.timestamp(now + datetime.timedelta(minutes=30))
        if target > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except(RuntimeError, KeyError):
        return response


@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(redirect('/'))
    unset_jwt_cookies(response)
    return response


@app.route('/main', methods=['GET'])
def main():
    now = "main"
    return render_template('signin.j2', current_time=now)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.j2')

    id = request.form["id"]
    exist = bool(db.users.find_one({"id": id}))
    if exist == True:
        flash("이미 가입된 아이디입니다.")
        return render_template('signup.j2')

    # Form Data 유효성 검사
    if request.form["id"] == '':
        return make_response("아이디를 입력해주세요")
    if request.form["pw"] != "" or request.form["pw_check"]:
        return make_response("비밀번호를 입력해주세요.")
    if request.form["pw"] != request.form["pw_check"]:
        return make_response("입력하신 비밀번호가 다릅니다.")
    if request.form["gisu"] == '':
        return make_response("기수를 선택해주세요")

    # 여기서 부터는 POST 로직
    hash_pw = hashlib.sha256(request.form["pw"].encode('utf-8')).hexdigest()
    request_dto = get_user_request_dto(hash_pw)

    # AWS S3로 이미지 URL 생성 필요
    f = request.files['imgUrl']

    file_name = secure_filename(f.filename)
    f.save(file_name)
    file_path = file_name
    file_name = 'profile/' + request_dto.id
    content_type = f.content_type
    data = open(file_path, 'rb')
    s3_connection().Bucket(BUCKET_NAME).put_object(
        Key=file_name,
        Body=data,
        ContentType=content_type)
    img_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{file_name}"
    request_dto.set_url(img_url)
    os.remove(file_path)

    user = {
        'uuid': str(uuid.uuid4()),
        'id': request_dto.id,
        'pw': request_dto.password,
        'gisu': request_dto.gisu,
        'ban': request_dto.ban,
        'name': request_dto.name,
        'imgUrl': request_dto.imgUrl
    }

    db.users.insert_one(user)

    characters = list(db.characters.find({},{'_id':False}))
    characters_list = []
    for character in characters:
        characters_list.append(character['trait'].replace(u'\xa0',u''))
    return render_template('prosandcons_register.j2', id=user['uuid'], characters = characters_list)


def get_user_request_dto(hash_pw):
    request_dto = dto.UserSignupRequestDto(
        request.form["id"], hash_pw,
        request.form["gisu"], request.form["ban"],
        "", request.form["name"])
    return request_dto


@app.route('/checkup', methods=['POST'])
def checkup():
    id_receive = request.form["id_give"]
    exist = bool(db.users.find_one({"id": id_receive}))
    if exist == False:
        return jsonify({'exist': 'false'})
    else:
        return jsonify({'exist': 'true'})


@app.route('/user', methods=['POST'])
def post_pros_and_cons():
    id = request.form["user_id"]
    pros_request_dto = get_pros_request_dto()
    cons_request_dto = get_cons_request_dto()
    pros = {
        'id': id,  # FK 역할 수행
        'first': pros_request_dto.first,
        'second': pros_request_dto.second,
        'third': pros_request_dto.third,
        'fourth': pros_request_dto.fourth,
        'fifth': pros_request_dto.fifth,
    }
    cons = {
        'id': id,  # FK 역할 수행
        'first': cons_request_dto.first,
        'second': cons_request_dto.second,
        'third': cons_request_dto.third,
        'fourth': cons_request_dto.fourth,
        'fifth': cons_request_dto.fifth,
    }
    db.pros.insert_one(pros)
    db.cons.insert_one(cons)

    return render_template('signin.j2')


def get_pros_request_dto():
    pros_request_dto = dto.ProsRequestDto(
        request.form["pro_first"], request.form["pro_second"],
        request.form["pro_third"], request.form["pro_fourth"],
        request.form["pro_fifth"], )
    return pros_request_dto


def get_cons_request_dto():
    cons_request_dto = dto.ConsRequestDto(
        request.form["con_first"], request.form["con_second"],
        request.form["con_third"], request.form["con_fourth"],
        request.form["con_fifth"], )
    return cons_request_dto


@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    # 모든 User 불러오기 => 해당 유저의 UUID, 이름, 기수 불러오기
    global user_response_dto
    target_uuid_list = []
    user_dto_list = []
    for x in db.users.find({}, {"uuid": 1, "ban": 1, "name": 1, "imgUrl": 1}):
        target_uuid_list.append(x["uuid"])
        user_response_dto = dto.UserResponseDto(x["uuid"], x["ban"], x["name"], x["imgUrl"], "", "", "", "")
        user_dto_list.append(user_response_dto)

    current_users_num = len(target_uuid_list)
    for i in range(current_users_num):
        for x in db.pros.find({"id": target_uuid_list[i]}, {"first": 1, "second": 1}):
            user_dto_list[i].set_pros(x["first"], x["second"])
        for x in db.cons.find({"id": target_uuid_list[i]}, {"first": 1, "second": 1}):
            user_dto_list[i].set_cons(x["first"], x["second"])

    return render_template('users.j2', user_list=user_dto_list)


@app.route('/user/<id>', methods=['GET'])
@jwt_required()
def get_user_detail(id):
    response_dto = dto.UserDetailResponseDto()
    name = db.users.find_one({"uuid": id}, {"name"})['name']
    for x in db.pros.find({"id": id}, {
        "first": 1,
        "second": 1,
        "third": 1,
        "fourth": 1,
        "fifth": 1,
    }):
        response_dto.set_pros(x["first"], x["second"], x["third"], x["fourth"], x["fifth"])
    for x in db.cons.find({"id": id}, {
        "first": 1,
        "second": 1,
        "third": 1,
        "fourth": 1,
        "fifth": 1,
    }):
        response_dto.set_cons(x["first"], x["second"], x["third"], x["fourth"], x["fifth"])
        response_dto.set_name(name)
    return render_template('result.j2', data=response_dto)


@app.route('/update', methods=['GET', 'POST'])
@jwt_required()
def update_user():
    id = get_jwt_identity()
    find_user = db.users.find_one({"id": id}, {"uuid": 1})
    target_uuid = find_user["uuid"]
    pros = db.pros.find_one({"id": target_uuid}, {"first": 1, "second": 1, "third": 1, "fourth": 1, "fifth": 1})
    cons = db.cons.find_one({"id": target_uuid}, {"first": 1, "second": 1, "third": 1, "fourth": 1, "fifth": 1})
    find_user_info = dto.UserDetailResponseDto()
    find_user_info.set_pros(
        pros["first"], pros["second"], pros["third"], pros["fourth"], pros["fifth"],
    )
    find_user_info.set_cons(
        cons["first"], cons["second"], cons["third"], cons["fourth"], cons["fifth"],
    )
    if request.method == 'GET':
        response = make_response(render_template("prosandcons_update.j2", pros=pros, cons=cons))
        return response

    update_request_dto = dto.UserUpdateRequestDto(request.form['pro_first'], request.form['pro_second'],
                                                  request.form['pro_third'], request.form['pro_fourth'],
                                                  request.form['pro_fifth'], request.form['con_first'],
                                                  request.form['con_second'], request.form['con_third'],
                                                  request.form['con_fourth'], request.form['con_fifth'])
    print(find_user_info.pros_make_list())
    print(update_request_dto.pros_make_list())
    print(update_request_dto.pros_make_list() == find_user_info.pros_make_list())

    if find_user_info.pros_make_list() == update_request_dto.pros_make_list() and \
            find_user_info.cons_make_list() == update_request_dto.cons_make_list():
        response = make_response("장점 또는 단점 중 데이터의 변경이 필요합니다.")
        return response

    update_pros(find_user_info, target_uuid, update_request_dto)
    update_cons(find_user_info, target_uuid, update_request_dto)
    response = make_response(redirect("/users"))
    return response


def update_pros(find_user_info, target_uuid, update_request_dto):
    if find_user_info.first_pro != update_request_dto.first_pro:
        db.pros.update_one({"id": target_uuid}, {"$set": {"first": request.form['pro_first']}})
    if find_user_info.second_pro != update_request_dto.second_pro:
        db.pros.update_one({"id": target_uuid}, {"$set": {"second": request.form['pro_second']}})
    if find_user_info.third_pro != update_request_dto.third_pro:
        db.pros.update_one({"id": target_uuid}, {"$set": {"third": request.form['pro_third']}})
    if find_user_info.fourth_pro != find_user_info.fourth_pro:
        db.pros.update_one({"id": target_uuid}, {"$set": {"fourth": request.form['pro_fourth']}})
    if find_user_info.fifth_pro != find_user_info.fifth_pro:
        db.pros.update_one({"id": target_uuid}, {"$set": {"fifth": request.form['pro_fifth']}})


def update_cons(find_user_info, target_uuid, update_request_dto):
    if find_user_info.first_con != update_request_dto.first_con:
        db.cons.update_one({"id": target_uuid}, {"$set": {"first": request.form['con_first']}})
    if find_user_info.second_con != update_request_dto.second_con:
        db.cons.update_one({"id": target_uuid}, {"$set": {"second": request.form['con_second']}})
    if find_user_info.third_con != update_request_dto.third_con:
        db.cons.update_one({"id": target_uuid}, {"$set": {"third": request.form['con_third']}})
    if find_user_info.fourth_con != find_user_info.fourth_con:
        db.cons.update_one({"id": target_uuid}, {"$set": {"fourth": request.form['con_fourth']}})
    if find_user_info.fifth_con != find_user_info.fifth_con:
        db.cons.update_one({"id": target_uuid}, {"$set": {"fifth": request.form['con_fifth']}})


@app.route('/user', methods=['DELETE'])
@jwt_required()
def delete_user():
    id = get_jwt_identity()
    db.users.delete_one({'id':id})
    return jsonify ({'result': 'success'})


@app.route('/users/<group>', methods=['GET'])
def get_user_class(group):

    global user_response_dto
    target_uuid_list = []
    user_dto_list = []
    for x in db.users.find({"ban":group}, {"uuid": 1, "ban": 1, "name": 1, "imgUrl": 1}):
        target_uuid_list.append(x["uuid"])
        user_response_dto = dto.UserResponseDto(x["uuid"], x["ban"], x["name"], x["imgUrl"], "", "", "", "")
        user_dto_list.append(user_response_dto)

    current_users_num = len(target_uuid_list)
    for i in range(current_users_num):
        for x in db.pros.find({"id": target_uuid_list[i]}, {"first": 1, "second": 1}):
            user_dto_list[i].set_pros(x["first"], x["second"])
        for x in db.cons.find({"id": target_uuid_list[i]}, {"first": 1, "second": 1}):
            user_dto_list[i].set_cons(x["first"], x["second"])

    return render_template('users.j2', user_list=user_dto_list)


if __name__ == '__main__':
    app.run()