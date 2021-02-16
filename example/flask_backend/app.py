from . import app, db, register_endpoints, register_blueprints, setup_acl
from sqlalchemy_utils import database_exists, create_database, drop_database

db.init_app(app)
register_blueprints(app)
register_endpoints(app)
engine = db.get_engine(app)

if not database_exists(engine.url):
    print(' * Creating database...')
    db.create_all(app=app)
    create_database(engine.url)
else:
    print(' * Database already exist...')

setup_acl(engine=db.get_engine(app))
