from flask import request, jsonify, Response, json
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from .models import *
from .serializers import *
from .utils import validate_request
from .auth import http_auth


class BaseAPI(MethodView):

    Model = None
    Schema = None
    decorators = [validate_request, http_auth.login_required]

    def get(self, id):
        if id is not None:
            object = self.Model.query.get(id)
            serializer = self.Schema(many=False)
            # TODO: error 404 handle??
            return jsonify(serializer.dump(object))
        else:
            objects = self.Model.query.all()
            serializer = self.Schema(many=True)
            return jsonify(serializer.dump(objects))

    def post(self):
        try:
            object = self.Model(**request.json)
            db.session.add(object)
            db.session.commit()
            return self.Schema().jsonify(object)
        except IntegrityError:
            db.session.rollback()
            return Response(json.dumps({'msg': 'cannot post object!'}), 400, mimetype='application/json')

    def delete(self, id):
        object = self.Model.query.get(id)
        if not object:
            return Response(json.dumps({'msg': 'cannot find object!'}), 404, mimetype='application/json')

        try:
            db.session.delete(object)
            db.session.commit()
            return self.Schema().jsonify(object)
        except IntegrityError:
            db.session.rollback()
            return Response(json.dumps({'msg': 'cannot delete object!'}), 400, mimetype='application/json')

    def put(self, id):
        object = self.Model.query.get(id)
        if not object:
            return Response(json.dumps({'msg': 'cannot find object!'}), 404, mimetype='application/json')

        try:
            object.update(**request.json)
            db.session.add(object)
            db.session.commit()
            return self.Schema().jsonify(object)
        except IntegrityError:
            db.session.rollback()
            return Response(json.dumps({'msg': 'cannot update object!'}), 400, mimetype='application/json')


class SalariesAPI(BaseAPI):
    Model = SalaryModel
    Schema = SalarySchema

class CustomersAPI(BaseAPI):
    Model = CustomerModel
    Schema = CustomerSchema

class OrdersAPI(BaseAPI):
    Model = OrderModel
    Schema = OrderSchema

class ArticlesAPI(BaseAPI):
    Model = ArticleModel
    Schema = ArticleSchema

class BoxesAPI(BaseAPI):
    Model = BoxModel
    Schema = BoxSchema

class ContentsAPI(BaseAPI):
    Model = ContentModel
    Schema = ContentSchema
