'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: server.py

@time: 2017/3/27 14:11

@desc: Ohlife Server

'''

import atexit
import logging
import traceback
import uuid
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

import arrow
import dateutil.parser
import flask
import flask_login
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_jwt import JWT, jwt_required, current_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimestampSigner, URLSafeSerializer, BadSignature
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy_utils import PasswordType

try:
    from helpers import credential, send_local_mail, render
except ImportError:
    from server.helpers import credential, send_local_mail, render
try:
    import ohlife
except ImportError:
    import server.ohlife


# jwt authenticate
def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user.password == password:
        return user


def identity(payload):
    session_id = payload['identity']
    return User.query.filter_by(session_id=session_id).first()


def create_app(database_uri, debug=False):
    app = Flask(__name__)
    app.debug = debug
    # set up your database
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=25)
    app.secret_key = credential["secret_key"]
    # add your modules
    db.init_app(app)
    # other setup tasks
    return app


# Sqlalchemy
db = SQLAlchemy()
app = create_app("sqlite:///./dbdir/ohlife.db", True)
# flask-jwt
jwt = JWT(app, authenticate, identity)
# flask-admin
admin = Admin(app, name='ohlife', template_mode='bootstrap3')
# flask-login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
# itsdangerous
url_serializer = URLSafeSerializer(app.config["SECRET_KEY"])
save_signer = TimestampSigner(app.config["SECRET_KEY"], salt="save")
unsub_signer = TimestampSigner(app.config["SECRET_KEY"], salt="unsub")
# flask-limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["30 per minute", "10 per second"]
)
# logging
handler = RotatingFileHandler('foo.log', maxBytes=100000, backupCount=3)
handler.setLevel(logging.ERROR)

app.logger.addHandler(handler)
# APScheduler
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
    # 'default': MemoryJobStore()
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
scheduler.start()


@app.after_request
def after_request(response):
    try:
        user_name = current_identity.username
    except AttributeError:
        user_name = "User didn't log in"
    try:
        payload = flask.request.get_json();
    except AttributeError:
        payload = "No payload"
    app.logger.info(
        """
        Time:      {time}
        Request:   {method} {path}
        IP:        {ip}
        Agent:     {agent_platform} | {agent_browser} {agent_browser_version}
        Raw Agent: {agent}
        User:      {user_name}
        Payload:   {payload}
        """.format(
            time=arrow.utcnow().format("YYYY-MM-DD:HH:mm:ss ZZ"),
            method=flask.request.method,
            path=flask.request.path,
            ip=flask.request.remote_addr,
            agent_platform=flask.request.user_agent.platform,
            agent_browser=flask.request.user_agent.browser,
            agent_browser_version=flask.request.user_agent.version,
            agent=flask.request.user_agent.string,
            payload=payload,
            user_name=user_name))
    return response


@app.errorhandler(Exception)
def exceptions(e):
    try:
        user_name = current_identity.username
    except AttributeError:
        user_name = "User didn't log in"
    try:
        payload = flask.request.get_json()
    except AttributeError:
        payload = "No payload"
    tb = traceback.format_exc()
    app.logger.error(
        """
        Time:      {time}
        Request:   {method} {path}
        IP:        {ip}
        Agent:     {agent_platform} | {agent_browser} {agent_browser_version}
        Raw Agent: {agent}
        Exception: {current_exception}
        User:      {user_name},
        Payload:   {payload}
        """.format(
            time=arrow.utcnow().format("YYYY-MM-DD:HH:mm:ss ZZ"),
            method=flask.request.method,
            path=flask.request.path,
            ip=flask.request.remote_addr,
            agent_platform=flask.request.user_agent.platform,
            agent_browser=flask.request.user_agent.browser,
            agent_browser_version=flask.request.user_agent.version,
            current_exception=tb,
            user_name=user_name,
            payload=payload,
            agent=flask.request.user_agent.string))

    return e
    # try:
    #     return e.status_code
    # except ValueError or AttributeError:
    #     return e


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
    active_status = db.Column("active_status", db.Boolean, default=True)
    authenticate_status = db.Column("authenticate_status", db.Boolean, default=False)
    schedule_task_id = db.Column("schedule_task_id", db.String(36))

    def __init__(self, username, password, email):
        self.user_id = str(uuid.uuid1())
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()
        self.session_id = str(uuid.uuid1())
        self.is_admin = False
        self.active_status = True
        self.authenticate_status = False

    def __repr__(self) -> str:
        return "<User %r>" % self.username

    @property
    def is_active(self):
        return self.active_status

    # for flask-jwt
    @property
    def id(self):
        return self.session_id

    def get_id(self):
        return self.session_id

    @property
    def is_authenticated(self):
        return self.active_status

    @property
    def is_anonymous(self):
        return super().is_anonymous()


class Entries(db.Model):
    __tablename__ = "entries"
    entry_id = db.Column('entry_id', db.String(32), primary_key=True)
    time = db.Column('time', db.String(24))
    text = db.Column('text', db.String(20))
    user_id = db.Column("user_id", db.String(32), db.ForeignKey("users.user_id"), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "entry_id": self.entry_id,
            "time": self.time,
            "text": self.text
        }

    def __init__(self, text, user_id):
        self.entry_id = str(uuid.uuid1())
        self.time = str(arrow.utcnow().format("YYYY-MM-DD"))
        self.text = text
        self.user_id = user_id

    def __init__(self, time, text, user_id):
        self.entry_id = str(uuid.uuid1())
        self.time = time
        self.text = text
        self.user_id = user_id


class OhlifeModelView(sqla.ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return flask.redirect(flask.url_for('home', next=flask.request.url))


# flaks-admin
admin.add_view(OhlifeModelView(User, db.session))
admin.add_view(OhlifeModelView(Entries, db.session))


@app.route('/checkauth')
@jwt_required()
def protected():
    if current_identity.authenticate_status is False:
        return "Not Active"
    else:
        return "Authorization Passed"


@app.route('/get_all_entries')
@jwt_required()
def get_entries():
    user_entries = Entries.query.filter_by(user_id=current_identity.user_id).all()
    json_result = flask.jsonify([entry.serialize for entry in user_entries])
    return json_result


@app.before_first_request
def initialization():
    """
    Initialization
    """
    db.create_all()
    # user = User(credential["admin_name"], credential["admin_password"], credential["admin_email"])
    # db.session.add(user)
    # db.session.commit()
    # entry = Entries("text", user.user_id)
    # db.session.add(entry)
    # db.session.commit()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Add support for foreign key , listening on connect event
    :param dbapi_connection:
    :param connection_record:
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@app.route('/login', methods=["GET", "POST"])
def home():
    """
    web login
    :return:
    """
    if flask.request.method == 'POST':
        email = flask.request.form['email']
        password = flask.request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is not None:
            if user.password == password:
                flask_login.login_user(user)
                return flask.redirect("/admin")
            else:
                return "Wrong Password"
        else:
            return "Wrong Username"
    else:
        return flask.render_template("login.html")


@login_manager.user_loader
def user_loader(session_id):
    return User.query.filter_by(session_id=session_id).first()


@app.route('/save', methods=['GET', 'POST'])
def email_login():
    """
    login check
    :return:
    """
    if flask.request.method == 'POST':
        json_request = flask.request.get_json()
        if json_request is not None:
            print(json_request)
            html = json_request["html"]
            soup = BeautifulSoup(html, "html.parser")
            try:
                save_key = soup.find(id="save_key").text.strip()
                # session_id will expire after 24 hours
                session_id = save_signer.unsign(save_key, max_age=86400)
                session_id = bytes.decode(session_id)
                user = User.query.filter_by(session_id=session_id).first()
                if user is not None:
                    flask.session["entry"] = soup.select('div[style]')[0].text
                    flask.session["user_id"] = user.user_id
                    flask_login.login_user(user)
                    return flask.redirect(flask.url_for('protected_save'))
                else:
                    flask.abort(404)
            except:
                flask.abort(500)


@app.route('/protected')
@flask_login.login_required
def protected_save():
    """
    after approved , save text to entries table
    """
    today = arrow.now().format('YYYY-MM-DD')
    entry = flask.session["entry"]
    user_id = flask.session["user_id"]
    print(entry)
    print(user_id)
    db_entry = Entries.query.filter_by(time=today).first()
    if db_entry is None:
        entry = Entries(today, entry, user_id)
        db.session.add(entry)
    else:
        db_entry.text = db_entry.text + "\n" + entry
    db.session.commit()
    return "Save Success"


@app.route('/logout')
def logout():
    """
    logout
    :return:
    """
    flask_login.logout_user()
    return 'Logged out'


@app.route('/entries_delete', methods=['POST'])
@jwt_required()
def delete_entry():
    if flask.request.method == 'POST':
        item = flask.request.get_json()
        entry = Entries.query.filter_by(entry_id=item["entry_id"]).first()
        print(entry)
        db.session.delete(entry)
        # db.session.commit()
        return "Delete Done"


@app.route('/entries_create', methods=['POST'])
@jwt_required()
def create_entry():
    if flask.request.method == 'POST':
        item = flask.request.get_json()
        diary_time = dateutil.parser.parse(item["time"])
        diary_time = diary_time.strftime("%Y-%m-%d")
        tmp_entry = Entries.query.filter_by(time=diary_time).first()
        if tmp_entry is not None:
            tmp_entry.text = str(tmp_entry.text) + "\n" + item["text"]
            # db.sessoin.commit()
            return flask.jsonify(tmp_entry.serialize)
        else:
            entry = Entries(diary_time, item["text"], current_identity.user_id)
            db.session.add(entry)
            # db.sessoin.commit()
            return flask.jsonify(entry.serialize)


# @app.route('/test')
# @jwt_required()
# def test():
#     # setting scheduled task
#     job = scheduler.add_job(
#         func=task_test,
#         trigger=IntervalTrigger(seconds=5),
#         id=current_identity.user_id,
#         name=current_identity.username + "'s scheduled task",
#         replace_existing=True)
#     return "Scheduled work started."

@app.route('/register', methods=['POST'])
@limiter.limit("5/day", exempt_when=lambda: current_identity.is_admin)
def register():
    """
    register user using restuful api
    :return:
    """
    request = flask.request.get_json()
    user_email = request["email"]
    user_password = request["password"]
    user = User(username=user_email, password=user_password, email=user_email)
    context = {
        "active_url": flask.url_for("active_user", payload=url_serializer.dumps(user.session_id), _external=True),
        "name": user.username
    }
    html_rendered = render("confirm.html", context)
    send_local_mail([user.email], "ohlife@loveblu.cn", "Ohlife Confirmation", html_rendered
                    , username=credential["smtp_username"], password=credential["smtp_password"],
                    server=credential["smtp_server"], files=[])
    db.session.add(user)
    db.session.commit()
    return "OK"


@app.route('/resent_activation')
@jwt_required()
@limiter.limit("5/day")
def resent_activation_email():
    """
    resent activate email to user
    :return:
    """
    user = current_identity
    if user.authenticate_status is False:
        context = {
            "active_url": flask.url_for("active_user", payload=url_serializer.dumps(user.session_id), _external=True),
            "name": user.username
        }
        html_rendered = render("confirm.html", context)
        send_local_mail([user.email], "ohlife@loveblu.cn", "Ohlife Confirmation", html_rendered
                        , username=credential["smtp_username"], password=credential["smtp_password"],
                        server=credential["smtp_server"], files=[])
        return "200"
    else:
        return flask.abort(404)


def send_schedule_email(user_id):
    """
    send scheduled mail
    :param user_id:user id
    :return:
    """
    print("fuck the world")
    # user = server.User.query.filter_by(user_id=user_id).get_or_404()
    # user_wrapper = [user]
    # user_text_list = ohlife.get_entry(user_wrapper)
    # ohlife.send_mail(user_text_list)


@app.route('/activate/<payload>')
def active_user(payload):
    """
    change user's authentication_status
    :param payload:
    :return:
    """
    try:
        session_id = url_serializer.loads(payload)
    except BadSignature:
        flask.abort(404)
    user = User.query.filter_by(session_id=session_id).first_or_404()
    if user.authenticate_status is True and False:
        return "Link expired.Don't use it."
    else:
        # setting scheduled task
        job = scheduler.add_job(
            # func=lambda: send_schedule_email(user.user_id),
            func=send_schedule_email,
            args=[user.user_id],
            trigger='cron',
            hour=10,
            timezone=credential["timezone"],
            id=user.user_id,
            name=user.username + "'s scheduled task",
            replace_existing=True)
        user.schedule_task_id = job.id
        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

        user.authenticate_status = True
        db.session.commit()
        return "User Activated"


@login_manager.unauthorized_handler
def unauthorized_handler():
    """
    deal with unauthorised request
    :return:
    """
    return 'Unauthorized'


if __name__ == '__main__':  # pragma: no cover
    app.run(credential["address"], port=int(credential["port"]), debug=True)
