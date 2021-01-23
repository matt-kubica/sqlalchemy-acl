from flask import Blueprint
from . import db


auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return 'hellno'