import os, hashlib, binascii
from flask import Blueprint, request, Response, json
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as TokenSerializer
from sqlalchemy.exc import IntegrityError

from sqlalchemy_acl import ACL

from . import app
from .models import UserModel


auth = Blueprint('auth', __name__)
token_serializer = TokenSerializer(app.config['SECRET_KEY'], expires_in=3600)
http_auth = HTTPTokenAuth('Bearer')
authorized_tokens = {}



def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    hash = binascii.hexlify(hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000))
    return (salt + hash).decode('ascii')


def verify_password(stored, provided):
    stored_salt = stored[:64]
    stored_hash = stored[64:]
    hash = hashlib.pbkdf2_hmac('sha512', provided.encode('utf-8'), stored_salt.encode('ascii'), 100000)
    hash = binascii.hexlify(hash).decode('ascii')
    return stored_hash == hash


# helper function for creating token response
def create_token(request, hash):
    credentials = {
        'username': request.json['username'],
        'password_hash': hash,
    }
    # when token is generated it is also added to authorized_tokens dict
    token = token_serializer.dumps(credentials).decode('utf-8')
    authorized_tokens[request.json['username']] = token
    return Response(json.dumps({'token': token}), 200, mimetype='application/json')


# required function that returns user-related serialized data
# when token is valid, otherwise returns False
@http_auth.verify_token
def verify_token(token):
    try:
        # check out if given token is already saved to authorized tokens
        if {token} & set(authorized_tokens.values()):
            return token_serializer.loads(token)
        else:
            return False
    except:
        return False


# custom error handler
@http_auth.error_handler
def error_handler(status):
    return Response(json.dumps({'msg': 'unauthorized!'}), 401, mimetype='application/json')


@auth.route('/register', methods=['POST'])
def register():
    try:
        password_hash = hash_password(request.json['password'])
        # create new user, add to associated access-level
        user = UserModel(username=request.json['username'], email=request.json['email'],
                         password_hash=password_hash)
        access_level = ACL.AccessLevels.get(role_description=request.json['access_level'])
        ACL.Users.add([user], access_level)
        return create_token(request, password_hash)
    except IntegrityError:
        ACL.inner_session.rollback()
        return Response(json.dumps({'msg': 'provided user already exist!'}), 400, mimetype='application/json')


@auth.route('/login', methods=['POST'])
def login():
    user = ACL.Users.get(username=request.json['username'])
    if user is None:
        return Response(json.dumps({'msg': 'bad request!'}), 400, mimetype='application/json')

    if verify_password(user.password_hash, request.json['password']):
        return create_token(request, user.password_hash)
    else:
        return Response(json.dumps({'msg': 'unauthorized!'}), 401, mimetype='application/json')



# logout endpoint - user need to provide token in order to log out
@auth.route('/logout', methods=['POST'])
@http_auth.login_required
def logout():
    # get token out of headers
    token = request.headers['Authorization'].replace('Bearer ', '')
    # get credentials based on token, remove token from authorized tokens
    credentials = token_serializer.loads(token)
    authorized_tokens.pop(credentials['username'])
    return Response(json.dumps({'msg': 'logged out!'}), 200, mimetype='application/json')




@auth.route('/hello', methods=['GET'])
@http_auth.login_required
def test():
    return Response(json.dumps({'msg': 'hello {0}!'.format(http_auth.current_user()['username'])}), 200, mimetype='application/json')
