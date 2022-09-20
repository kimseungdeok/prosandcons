import hashlib
from flask import Flask, render_template, make_response, request
import datetime
import uuid
from pymongo import MongoClient

import dto

app = Flask(__name__)

client = MongoClient('mongodb://15.164.217.239', 27017, username="root", password="root")
db = client.prosncons


@app.route('/', methods=['GET'])
def get_main_page():
    now = datetime.datetime.now()
    return render_template('test.j2', current_time=now)


@app.route('/login', methods=['POST'])
def login():
    response = make_response()
    return response


@app.route('/main', methods=['GET'])
def main():
    now = "main"
    return render_template('test.j2', current_time=now)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        print("this is sign-up GET log")
        return render_template('signup.j2')
    # 여기서 부터는 POST 로직
    hash_pw = hashlib.sha256(request.form["pw"].encode('utf-8')).hexdigest()
    request_dto = get_user_request_dto(hash_pw)
    # AWS S3로 이미지 URL 생성 필요
    user = {
        'id': str(uuid.uuid4()),
        'userId': request_dto.id,
        'pw': request_dto.password,
        'gisu': request_dto.gisu,
        'ban': request_dto.ban,
    }
    db.users.insert_one(user)
    return render_template('prosandcons_register.j2', id=user['id'])


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
        'id': id,#FK 역할 수행
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

    return render_template('test.j2')


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
    return render_template('test.j2', current_time=now)


@app.route('/user/<id>', methods=['PATCH'])
def update_user():
    now = "users"
    return render_template('test.j2', current_time=now)


@app.route('/user/<id>', methods=['DELETE'])
def delete_user():
    now = "users"
    return render_template('test.j2', current_time=now)


if __name__ == '__main__':
    app.run()
