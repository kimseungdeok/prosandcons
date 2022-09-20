import hashlib
from flask import Flask, render_template, request, jsonify, make_response
import datetime
import uuid
from pymongo import MongoClient
from flask_jwt_extended import *

import config
import dto

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    JWT_SECRET_KEY=config.JWT_SECRET_KEY
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(seconds=15)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False

client = MongoClient('mongodb://15.164.217.239', 27017, username="root", password="root")
db = client.prosncons
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
        response = make_response(render_template("main.j2"))
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
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@app.route('/main', methods=['GET'])
def main():
    now = "main"
    return render_template('signin.j2', current_time=now)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        # print("this is sign-up GET log")
        return render_template('signup.j2')
    # 여기서 부터는 POST 로직
    hash_pw = hashlib.sha256(request.form["pw"].encode('utf-8')).hexdigest()
    request_dto = get_user_request_dto(hash_pw)
    # AWS S3로 이미지 URL 생성 필요
    user = {
        'uuid': str(uuid.uuid4()),
        'id': request_dto.id,
        'pw': request_dto.password,
        'gisu': request_dto.gisu,
        'ban': request_dto.ban,
    }
    db.users.insert_one(user)
    return render_template('prosandcons_register.j2', id=user['uuid'])


def get_user_request_dto(hash_pw):
    request_dto = dto.UserSignupRequestDto(request.form["id"], hash_pw, request.form["gisu"],
                                           request.form["ban"], request.form["imgUrl"])
    return request_dto


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
def get_users():
    now = "users"
    return render_template('signin.j2', current_time=now)


@app.route('/user/<id>', methods=['PATCH'])
def update_user():
    now = "users"
    return render_template('signin.j2', current_time=now)


@app.route('/user/<id>', methods=['DELETE'])
def delete_user():
    now = "users"
    return render_template('signin.j2', current_time=now)


if __name__ == '__main__':
    app.run()
