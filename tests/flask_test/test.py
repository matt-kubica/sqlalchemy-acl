import functools, sys, os
sys.path.insert(0,'../..')

from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError

from sqlalchemy_acl import ACL
from sqlalchemy_acl.models import UserModel


DB_FILENAME = 'db.sqlite'
ACL_CONFIG_FILENAME = 'acl-config.yaml'
DELETE_DB = True


### --- INIT SECTION ------------------------------------------------------------------------------
app = Flask(__name__)

# config
if os.path.exists(DB_FILENAME) and DELETE_DB: os.remove(DB_FILENAME)
DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), DB_FILENAME)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
### -----------------------------------------------------------------------------------------------



### --- MODELS SECTION ----------------------------------------------------------------------------
db = SQLAlchemy(app)

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

# creating tables in db
db.create_all()
### -----------------------------------------------------------------------------------------------


### --- SERIALIZERS SECTION -----------------------------------------------------------------------
ma = Marshmallow(app)

# defining serializer schema
class ExemplarySchema(ma.Schema):
    class Meta:
        fields = ('id', 'string_field', 'integer_field')

# init schemas
std_schema = ExemplarySchema(many=False)
mul_schema = ExemplarySchema(many=True)
### -----------------------------------------------------------------------------------------------



### --- ACL SETUP SECTION -------------------------------------------------------------------------
ACL.setup(db.engine, ACL_CONFIG_FILENAME)
ACL.Users.add([UserModel(username='admin')], ACL.root_access_level)

def validate_request(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):

        ACL.set_user(ACL.Users.get(username='admin'))

        return f(*args, **kwargs)
    return decorated_function
### -----------------------------------------------------------------------------------------------



### --- ENDPOINTS SECTION -------------------------------------------------------------------------
# get all exemplary objects
@app.route('/exemplary-object', methods=['GET'])
@validate_request
def get_objects():
    objects = ExemplaryModel.query.all()
    result = mul_schema.dump(objects)
    return jsonify(result)

# get single exemplary object with given id
@app.route('/exemplary-object/<id>', methods=['GET'])
@validate_request
def get_object(id):
    object = ExemplaryModel.query.get(id)
    result = std_schema.dump(object)
    return jsonify(result)

# post single exemplary object
@app.route('/exemplary-object', methods=['POST'])
@validate_request
def post_object():
    try:
        object = ExemplaryModel(
            request.json['id'], request.json['string_field'], request.json['integer_field']
        )
        db.session.add(object)
        db.session.commit()
        return std_schema.jsonify(object)
    except IntegrityError:
        db.session.rollback()
        abort(400)

# update exemplary object with given id
@app.route('/exemplary-object/<id>', methods=['PUT'])
@validate_request
def update_object(id):
    object = ExemplaryModel.query.get(id)

    if not object:
        abort(404)

    object.string_field = request.json['string_field']
    object.integer_field = request.json['integer_field']

    try:
        db.session.add(object)
        db.session.commit()
        return std_schema.jsonify(object)
    except IntegrityError:
        db.session.rollback()
        abort(400)

# delete exemplary object with given id
@app.route('/exemplary-object/<id>', methods=['DELETE'])
@validate_request
def delete_object(id):
    object = ExemplaryModel.query.get(id)

    if not object:
        abort(404)

    try:
        db.session.delete(object)
        db.session.commit()
        return std_schema.jsonify(object)
    except IntegrityError:
        db.session.rollback()
        abort(400)
### -----------------------------------------------------------------------------------------------



# debug should be set to False in all cases because otherwise
# reload-thread is launched and ACL does not work in this case (yet)
if __name__ == '__main__':
    app.run(debug=False)