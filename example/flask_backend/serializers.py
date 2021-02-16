from flask_marshmallow import Marshmallow
from . import app
from .models import *

ma = Marshmallow(app)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        include_fk = True

class SalarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SalaryModel
        include_fk = True

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CustomerModel
        include_fk = True

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderModel
        include_fk = True

class ArticleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ArticleModel
        include_fk = True

class BoxSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BoxModel
        include_fk = True

class ContentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ContentModel
        include_fk = True