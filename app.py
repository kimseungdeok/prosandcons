from flask import Flask,render_template
import datetime

app = Flask(__name__)

@app.route('/', methods=['GET'])
def login():
    now = datetime.datetime.now()
    return render_template('test.j2',current_time = now)

@app.route('/main', methods=['GET'])
def main():
    now = "main"
    return render_template('test.j2',current_time = now)

@app.route('/signup', methods=['GET'])
def signup():
    now = "signup"
    return render_template('test.j2',current_time = now)

@app.route('/users', methods=['GET'])
def get_users():
    now = "users"
    return render_template('test.j2',current_time = now)

@app.route('/user/<id>', methods=['POST'])
def post_prosncons():
    now = "users"
    return render_template('test.j2',current_time = now)

@app.route('/user/<id>', methods=['PATCH'])
def update_user():
    now = "users"
    return render_template('test.j2',current_time = now)

@app.route('/user/<id>', methods=['DELETE'])
def delete_user():
    now = "users"
    return render_template('test.j2',current_time = now)

if __name__ == '__main__':
    app.run()
