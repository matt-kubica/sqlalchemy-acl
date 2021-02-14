import sys, os
sys.path.insert(0, '../..')

from flask import Flask as BaseFlask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


# extends flask with method that allows registering api endpoint in more optimal way
class Flask(BaseFlask):

    def register_api(self, view, endpoint, url, pk='id', pk_type='int'):
        view_func = view.as_view(endpoint)
        self.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET'])
        self.add_url_rule(url, view_func=view_func, methods=['POST'])
        self.add_url_rule('{0}<{1}:{2}>'.format(url, pk_type, pk), view_func=view_func,
                          methods=['GET', 'PUT', 'DELETE'])


# constants
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite') + '?check_same_thread=False'
ACL_CONFIG_PATH = os.path.join(BASE_DIR, 'acl-config.yaml')

# config
db = SQLAlchemy()
app = Flask(__name__)
app.app_context().push()
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-ultra-secret-key'


# helper methods
def register_blueprints(app):
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

def register_endpoints(app):
    from .api import SalariesAPI, CustomersAPI, OrdersAPI, ArticlesAPI, BoxesAPI, ContentsAPI
    app.register_api(SalariesAPI, 'salaries_api', '/salaries/')
    app.register_api(CustomersAPI, 'customers_api', '/customers/')
    app.register_api(OrdersAPI, 'orders_api', '/orders/')
    app.register_api(ArticlesAPI, 'articles_api', '/articles/')
    app.register_api(BoxesAPI, 'boxes_api', '/boxes/')
    app.register_api(ContentsAPI, 'contents_api', '/contents/')

def setup_acl(engine):
    from sqlalchemy_acl import ACL
    from .models import UserModel
    ACL.setup(engine, user_model=UserModel, access_levels_config=ACL_CONFIG_PATH)


