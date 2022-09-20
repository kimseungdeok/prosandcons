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
    request_dto = dto.UserSignupRequestDto(request.form["id"], hash_pw, request.form["gisu"],
                                           request.form["ban"], request.form["imgUrl"])
    # AWS S3로 이미지 URL 생성 필요

    user = {
        'id': str(uuid.uuid4()),
        'userId': request_dto.id,
        'pw': request_dto.password,
        'gisu': request_dto.gisu,
        'ban': request_dto.ban,
        'pros': None,
        'cons': None,
    }
    db.users.insert_one(user)
    return render_template('prosandcons_register.j2', id=user['id'])


@app.route('/user', methods=['POST'])
def post_prosncons():
    now = "users"
    return render_template('test.j2', current_time=now)


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
