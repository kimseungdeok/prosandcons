from flask import Flask, render_template, make_response, request
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


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        print("this is sign-up GET log")
        return render_template('signup.j2')
    # 여기서 부터는 POST 로직
    request_dto = dto.UserSignupRequestDto(request.form["id"], request.form["pw"], request.form["gisu"],
                                           request.form["ban"], request.form["imgUrl"])
    print(request_dto.id)
    print(request_dto.password)
    print(request_dto.gisu)
    print(request_dto.ban)
    print(request_dto.imgUrl)
    return render_template('prosAndCons.j2')


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
