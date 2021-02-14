import sys, os
sys.path.insert(0, '../..')

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite') + '?check_same_thread=False'
ACL_CONFIG_PATH = os.path.join(BASE_DIR, 'acl-config.yaml')

db = SQLAlchemy()
app = Flask(__name__)
app.app_context().push()
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-ultra-secret-key'



def register_api(app, view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET'])
    app.add_url_rule(url, view_func=view_func, methods=['POST'])
    app.add_url_rule('{0}<{1}:{2}>'.format(url, pk_type, pk), view_func=view_func, methods=['GET', 'PUT', 'DELETE'])


def register_blueprints(app):
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)


def register_endpoints(app):
    from .api import SalariesAPI, CustomersAPI, OrdersAPI, ArticlesAPI, BoxesAPI, ContentsAPI
    register_api(app, SalariesAPI, 'salaries_api', '/salaries/')
    register_api(app, CustomersAPI, 'customers_api', '/customers/')
    register_api(app, OrdersAPI, 'orders_api', '/orders/')
    register_api(app, ArticlesAPI, 'articles_api', '/articles/')
    register_api(app, BoxesAPI, 'boxes_api', '/boxes/')
    register_api(app, ContentsAPI, 'contents_api', '/contents/')



def setup_acl(engine):
    from sqlalchemy_acl import ACL
    from .models import UserModel
    ACL.setup(engine, user_model=UserModel, access_levels_config=ACL_CONFIG_PATH)


db.init_app(app)
register_blueprints(app)
register_endpoints(app)
db.create_all(app=app)
setup_acl(engine=db.get_engine(app))