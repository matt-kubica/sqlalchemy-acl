from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from acl import ACLQuery
import os



# app instance
app = Flask(__name__)

# database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# database initialization, with custom query class
db = SQLAlchemy(app, query_class=ACLQuery)



# model definition
class Wage(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.String(64), unique=True, nullable=False)
	amount = db.Column(db.Integer, unique=False, nullable=False)

	def __repr__(self):
		return '<Wage {0}:{1}:{2}>'.format(self.id, self.user, self.amount)



# will execute only if this file is entry point
if __name__ == '__main__':
	app.run(debug=True)