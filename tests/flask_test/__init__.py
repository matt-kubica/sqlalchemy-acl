import sys, os
sys.path.insert(0,'../..')
sys.path.insert(0,'..')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from sqlalchemy_acl import ACL

from random import randrange




def register_blueprints(app):
    from .auth import auth as auth_blueprint
    from .api import api as api_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(api_blueprint)


def setup_acl(engine, db):
    from .models import CustomUserModel, ExemplaryModel
    ACL.setup(engine, user_model=CustomUserModel, access_levels_config=ACL_CONFIG_ABS_PATH)
    root_level_objects = [
			ExemplaryModel(id=1, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=2, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=3, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=4, string_field='some_string', integer_field=randrange(100000)),
		]
    db.session.add_all(root_level_objects)
    db.session.commit()

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
DB_FILENAME = 'db.sqlite'
DB_ABS_PATH = os.path.join(ABS_PATH, DB_FILENAME)
ACL_CONFIG_FILENAME = 'acl-config.yaml'
ACL_CONFIG_ABS_PATH = os.path.join(ABS_PATH, ACL_CONFIG_FILENAME)
DELETE_DB = True


db = SQLAlchemy()
app = Flask(__name__)
app.app_context().push()
CORS(app, resources={r"/*": {"origins": "*"}})

if os.path.exists(DB_ABS_PATH) and DELETE_DB: os.remove(DB_ABS_PATH)
DATABASE_URI = 'sqlite:///' + DB_ABS_PATH + '?check_same_thread=False'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-ultra-secret-key'
db.init_app(app)
register_blueprints(app)
db.create_all(app=app)
setup_acl(engine=db.get_engine(app), db=db)





