import functools
from sqlalchemy_acl import ACL
from .auth import http_auth

def validate_request(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        credentials = http_auth.current_user()
        ACL.set_user(ACL.Users.get(**credentials))
        response = f(*args, **kwargs)
        ACL.unset_user()
        return response
    return decorated_function