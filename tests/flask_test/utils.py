import functools
from sqlalchemy_acl import ACL

def validate_request(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):

        ACL.set_user(ACL.Users.get(username='admin'))

        return f(*args, **kwargs)
    return decorated_function