### NOT TESTED WITH FLASK YET ###
### THIS IS OLD VERSION - NOT COMPATIBILE WITH CURRENT RELEASE OF SQLALCHEMY-ACL

import functools

import flask
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from sqlalchemy_acl import ACL
import os



# app instance
app = Flask(__name__)

# database config
DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# database initialization, with custom query class
db = SQLAlchemy(app, query_class=ACL.Query)

# init serializer
ma = Marshmallow(app)


# model definition
class Wage(db.Model):
    __tablename__ = 'wages'

    id = db.Column(db.Integer, primary_key=True)
    person = db.Column(db.String(64), unique=True, nullable=False)
    amount = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return '<Wage {0}:{1}:{2}>'.format(self.id, self.person, self.amount)


# defining serializer schema
class WageSchema(ma.Schema):
    class Meta:
        fields = ('id', 'person', 'amount')

# init schema
wages_schema = WageSchema(many=True)


# creating tables in db
# db.create_all()

# ACL setup
# engine is required argument
# user_model is optional argument, there is possibility to pass custom user model
# default user model is present in acl.py file
ACL.setup(db.get_engine())


def validate_request(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # for now something like that, hardcoded user setting
        # later set acl user according to logged user
        admin = db.session.query(ACL.UserModel).filter_by(id=1).scalar()
        ACL.set_user(admin)

        return f(*args, **kwargs)
    return decorated_function


@app.route('/wage', methods=['GET'])
@validate_request
def get_wages():
    wages = Wage.query.all()
    result = wages_schema.dump(wages)
    return jsonify(result)



# will execute only if this file is entry point
if __name__ == '__main__':
    app.run(debug=True)