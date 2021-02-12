from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import IntegrityError

from . import db
from .serializers import std_schema, mul_schema
from .models import ExemplaryModel
from .utils import validate_request
from .auth import http_auth


api = Blueprint('api', __name__)


# get all exemplary objects
@api.route('/exemplary-object', methods=['GET'])
@http_auth.login_required
@validate_request
def get_objects():
    objects = ExemplaryModel.query.all()
    result = mul_schema.dump(objects)
    return jsonify(result)

# get single exemplary object with given id
@api.route('/exemplary-object/<id>', methods=['GET'])
@http_auth.login_required
@validate_request
def get_object(id):
    object = ExemplaryModel.query.get(id)
    result = std_schema.dump(object)
    return jsonify(result)

# post single exemplary object
@api.route('/exemplary-object', methods=['POST'])
@http_auth.login_required
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
@api.route('/exemplary-object/<id>', methods=['PUT'])
@http_auth.login_required
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
@api.route('/exemplary-object/<id>', methods=['DELETE'])
@http_auth.login_required
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
