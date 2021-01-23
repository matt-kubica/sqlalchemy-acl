from flask_marshmallow import Marshmallow
from . import app

ma = Marshmallow(app)

# defining serializer schema
class ExemplarySchema(ma.Schema):
    class Meta:
        fields = ('id', 'string_field', 'integer_field')

# init schemas
std_schema = ExemplarySchema(many=False)
mul_schema = ExemplarySchema(many=True)