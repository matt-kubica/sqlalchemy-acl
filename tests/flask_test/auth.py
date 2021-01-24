from flask import Blueprint, request, abort, Response, json
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as TokenSerializer
from sqlalchemy.exc import IntegrityError

from sqlalchemy_acl import ACL

from . import  app
from .models import CustomUserModel


auth = Blueprint('auth', __name__)
token_serializer = TokenSerializer(app.config['SECRET_KEY'], expires_in=3600)
http_auth = HTTPTokenAuth('Bearer')


# helper function for creating token response
def create_token(request):
    credentials = {
        'username': request.json['username'],
        'password_hash': hash(request.json['password']),
    }
    token = token_serializer.dumps(credentials).decode('utf-8')
    return Response(json.dumps({'token': token}), 200, mimetype='application/json')


# required function that returns user-related serialized data
# when token is valid, otherwise returns False
@http_auth.verify_token
def verify_token(token):
    try:
        return token_serializer.loads(token)
    except:
        return False


@auth.route('/register', methods=['POST'])
def register():
    try:
        # create new user, add to associated access-level
        user = CustomUserModel(username=request.json['username'], email=request.json['email'],
                               password_hash=hash(request.json['password']))
        access_level = ACL.AccessLevels.get(role_description=request.json['access_level'])
        ACL.Users.add([user], access_level)
        return create_token(request)
    except IntegrityError:
        ACL.inner_session.rollback()
        abort(400)


@auth.route('/login', methods=['POST'])
def login():
    user = ACL.Users.get(username=request.json['username'],
                         password_hash=hash(request.json['password']))
    if not user: abort(401)
    return create_token(request)


@auth.route('/hello', methods=['GET'])
@http_auth.login_required
def test():
    return Response(json.dumps({'msg': 'hello {0}!'.format(http_auth.current_user()['username'])}), 200, mimetype='application/json')
