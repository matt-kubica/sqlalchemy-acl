import sys
sys.path.insert(0,'../..')
sys.path.insert(0,'..')

from sqlalchemy_acl.models import UserModelMixin

from . import db

class ExemplaryModel(db.Model):
    __tablename__ = 'testable-models'

    id = db.Column(db.Integer, primary_key=True)
    string_field = db.Column(db.String(64), unique=False, nullable=False)
    integer_field = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, id, string_field, integer_field):
        self.id = id
        self.string_field = string_field
        self.integer_field = integer_field

    def __repr__(self):
        return '<TestableModel {0}>'.format(self.id)


class CustomUserModel(UserModelMixin):
    email = db.Column(db.String(64), unique=False, nullable=False)
    password_hash = db.Column(db.String(128), unique=False, nullable=False)

    def __init__(self, email, password_hash, **kwargs):
        self.email = email
        self.password_hash = password_hash
        super().__init__(**kwargs)