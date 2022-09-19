from flask import Flask,render_template
import datetime

app = Flask(__name__)


@app.route('/')
def hello_world():
    now = datetime.datetime.now()
    return render_template('test.j2',current_time = now)


if __name__ == '__main__':
    app.run()
