from . import app, db, register_endpoints, register_blueprints, setup_acl


if __name__ == '__main__':


    app.run(debug=False)
