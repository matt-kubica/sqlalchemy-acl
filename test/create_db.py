from api import db, app
import os, sys

db_path = db.app.config['SQLALCHEMY_DATABASE_URI']


def create_db():
	db.create_all()
	models = [cls for cls in db.Model._decl_class_registry.values() if isinstance(cls, type) and issubclass(cls, db.Model)]
	print('Database created!\nPath: {0}\nModels: {1}'.format(db_path, models))



if __name__ == '__main__':

	if os.path.exists(db_path.replace('sqlite:///', '')):
		print('Database already exist...')
		ans = input('Do you wish to create new? [Y/N]: ')
		if ans.upper() == 'Y':
			create_db()
		else:
			sys.exit(0)
	else:
		create_db()








