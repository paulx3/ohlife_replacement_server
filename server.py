'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: server.py

@time: 2017/3/27 14:11

@desc: Ohlife 服务端

'''
import uuid
from datetime import datetime

import arrow
import flask
import flask_login
from bs4 import BeautifulSoup
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy_utils import PasswordType

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./dbdir/ohlife.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret string'
db = SQLAlchemy(app)
admin = Admin(app, name='ohlife', template_mode='bootstrap3')
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class User(db.Model, flask_login.UserMixin):
    __tablename__ = "users"
    user_id = db.Column('user_id', db.String(32), primary_key=True)
    username = db.Column('username', db.String(20), unique=False, index=True)
    password = db.Column("password", PasswordType(
        schemes=[
            'pbkdf2_sha512',
            'md5_crypt'
        ],
        deprecated=['md5_crypt']
    ))
    email = db.Column('email', db.String(50), unique=True, index=True)
    session_id = db.Column("session_id", db.String(32), unique=True)
    registered_on = db.Column('registered_on', db.DateTime)
    posts = db.relationship('Entries', backref='posts', lazy='dynamic')
    is_admin = db.Column("is_admin", db.Boolean, default=False)

    def __init__(self, user_id, username, password, email):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()
        self.session_id = None
        self.is_admin = False

    def __repr__(self) -> str:
        return "<User %r>" % self.username

    @property
    def is_active(self):
        return True

    def get_id(self):
        return self.user_id

    @property
    def is_authenticated(self):
        return self.is_admin

    @property
    def is_anonymous(self):
        return super().is_anonymous()


class Entries(db.Model):
    __tablename__ = "entries"
    entry_id = db.Column('entry_id', db.String(32), primary_key=True)
    time = db.Column('time', db.String(24))
    text = db.Column('text', db.String(20))
    user_id = db.Column("user_id", db.String(32), db.ForeignKey("users.user_id"), nullable=False)

    def __init__(self, entry_id, time, text, user_id):
        self.entry_id = entry_id
        self.time = time
        self.text = text
        self.user_id = user_id


class OhlifeModelView(sqla.ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return flask.redirect(flask.url_for('home', next=flask.request.url))


admin.add_view(OhlifeModelView(User, db.session))
admin.add_view(OhlifeModelView(Entries, db.session))


@app.before_first_request
def initialization():
    pass


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    用来打开对外键的支持，监听connect
    :param dbapi_connection: 
    :param connection_record: 
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@app.route('/login', methods=["GET", "POST"])
def home():
    if flask.request.method == 'POST':
        email = flask.request.form['email']
        password = flask.request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is not None:
            if user.password == password:
                flask_login.login_user(user)
                return "login ok"
            else:
                return "wrong password"
        else:
            return "login error"
    else:
        return flask.Response('''
           <form action="" method="post">
               <p><input type=text name=email>
               <p><input type=password name=password>
               <p><input type=submit value=Login>
           </form>
           ''')


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


# @login_manager.request_loader
# def load_user_from_header(request):
#     api_key = request.get_json()["key"]
#     if api_key:
#         user = User.query.filter_by(user_id=api_key).first()
#         if user:
#             return user
@app.route('/save', methods=['GET', 'POST'])
def email_login():
    """
    进行登陆验证
    :return: 
    """
    if flask.request.method == 'POST':
        json_request = flask.request.get_json()
        if json_request is not None:
            print(json_request)
            html = json_request["html"]
            soup = BeautifulSoup(html, "lxml")
            user_id = soup.find(id="save_key").text.strip()
            user = User.query.get_or_404(user_id)
            flask.session["entry"] = soup.select('div[style]')[0].text
            flask.session["user_id"] = user_id
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('protected_save'))


@app.route('/protected')
@flask_login.login_required
def protected_save():
    """
    验证通过后，进行存储
    """
    today = arrow.now().format('YYYY-MM-DD HH:mm:ss')
    entry = flask.session["entry"]
    user_id = flask.session["user_id"]
    print(entry)
    print(user_id)
    entry = Entries(str(uuid.uuid1()), today, entry, user_id)
    db.session.add(entry)
    db.session.commit()
    return "Save Success"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080, debug=True)
