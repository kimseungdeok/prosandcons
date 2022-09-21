from flask import Flask, render_template, make_response, request
from db_connection import s3_connection
from config import *
from werkzeug.utils import secure_filename
import datetime
import dto

app = Flask(__name__)


class User:
    def __init__(self, name, password, gisu, ban, image):
        self.name = name
        self.password = password
        self.gisu = gisu
        self.ban = ban
        self.image = image


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


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        print("this is sign-up GET log")
        return render_template('signup.j2')
    # 여기서 부터는 POST 로직
    else:
        request_dto = dto.UserSignupRequestDto(request.form["id"], request.form["pw"], request.form["gisu"],
                                            request.form["ban"], "")

        f = request.files['imgUrl']

        file_name = secure_filename(f.filename)
        f.save(file_name)

        file_path = file_name
        file_name = 'profile/'+ request_dto.id
        content_type = f.content_type
        data = open(file_path,'rb')
        s3_connection().Bucket(BUCKET_NAME).put_object(
            Key = file_name, 
            Body = data, 
            ContentType= content_type)

        img_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{file_name}"
        request_dto.set_url(img_url)
        return "success"


@app.route('/users', methods=['GET'])
def get_users():
    now = "users"
    return render_template('test.j2', current_time=now)


@app.route('/user/<id>', methods=['POST'])
def post_prosncons():
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
