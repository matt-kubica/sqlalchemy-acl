import functools, sys, os
sys.path.insert(0,'../..')
sys.path.insert(0,'..')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy_acl import ACL
from sqlalchemy_acl.models import UserModel


def register_blueprints(app):
    from .auth import auth as auth_blueprint
    from .api import api as api_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(api_blueprint)


ABS_PATH = os.path.abspath(os.path.dirname(__file__))
DB_FILENAME = 'db.sqlite'
DB_ABS_PATH = os.path.join(ABS_PATH, DB_FILENAME)
ACL_CONFIG_FILENAME = 'acl-config.yaml'
ACL_CONFIG_ABS_PATH = os.path.join(ABS_PATH, ACL_CONFIG_FILENAME)
DELETE_DB = True


db = SQLAlchemy()
app = Flask(__name__)

if os.path.exists(DB_ABS_PATH) and DELETE_DB: os.remove(DB_ABS_PATH)
DATABASE_URI = 'sqlite:///' + DB_ABS_PATH
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
register_blueprints(app)

db.create_all(app=app)
engine = db.get_engine(app)

ACL.setup(engine, ACL_CONFIG_ABS_PATH)
ACL.Users.add([UserModel(username='admin')], ACL.root_access_level)

