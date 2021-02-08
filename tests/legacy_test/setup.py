# narazie zmieniłem tylko setup dla YAML

import sys, os
import time
from subprocess import call
sys.path.insert(0,'..')


from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from sqlalchemy_acl import ACL
from sqlalchemy_acl.models import AccessLevelModel

from .models import Base


def setup_database(db_path):
	engine = create_engine(db_path, echo=False)
	Session = sessionmaker(bind=engine)
	session = Session()
	Base.metadata.create_all(bind=engine)
	return session, engine


class DefaultSetupMixin:

	DB_PATH = 'db.sqlite'
	WHOLE_DB_PATH = 'sqlite:///' + DB_PATH

	# noinspection PyArgumentList
	def setUp(self):
		self.session, self.engine = setup_database(DefaultSetupMixin.WHOLE_DB_PATH)
		ACL.setup(self.engine)

		# tabela z poziomami dostępu
		director_acl = AccessLevelModel(role_description='Executive Director', parent=ACL.root_access_level)
		project_manager_acl = AccessLevelModel(role_description='Project Manager', parent=director_acl)
		software_developer_acl = AccessLevelModel(role_description='Software Developer', parent=project_manager_acl)
		network_admin_acl = AccessLevelModel(role_description='Network Admin', parent=project_manager_acl)
		devops_acl = AccessLevelModel(role_description='Dev Ops', parent=project_manager_acl)
		software_dev_intern_acl = AccessLevelModel(role_description='Software Developer Intern', parent=software_developer_acl)
		network_admin_intern_acl = AccessLevelModel(role_description='Network Admin Intern', parent=network_admin_acl)

		ACL.AccessLevels.add([director_acl, project_manager_acl, software_developer_acl, network_admin_intern_acl,
							  devops_acl, software_dev_intern_acl, network_admin_intern_acl])

		# użytkownicy z odpowiednimi trybami dostępu (najlepiej po kilku na jeden tryb)
		ACL.Users.add([ACL.UserModel(username='admin1'), ACL.UserModel(username='admin2')],
					  ACL.root_access_level)
		ACL.Users.add([ACL.UserModel(username='manager1'), ACL.UserModel(username='manager2')],
					  project_manager_acl)
		ACL.Users.add([ACL.UserModel(username='software-dev1'), ACL.UserModel(username='software-dev2'),
					   ACL.UserModel(username='software-dev3'), ACL.UserModel(username='software-dev4')],
					  software_developer_acl)
		ACL.Users.add([ACL.UserModel(username='sd-intern1'), ACL.UserModel(username='sd-intern2'),
					   ACL.UserModel(username='sd-intern3'), ACL.UserModel(username='sd-intern4'),
					   ACL.UserModel(username='sd-intern5'), ACL.UserModel(username='sd-intern6')],
					  software_dev_intern_acl)
		ACL.Users.add([ACL.UserModel(username='network-admin1'), ACL.UserModel(username='network-admin2'),
					   ACL.UserModel(username='network-admin3'), ACL.UserModel(username='network-admin4')],
					  network_admin_acl)
		ACL.Users.add([ACL.UserModel(username='na-intern1'), ACL.UserModel(username='na-intern2'),
					   ACL.UserModel(username='na-intern3'), ACL.UserModel(username='na-intern4'),
					   ACL.UserModel(username='na-intern5'), ACL.UserModel(username='na-intern6')],
					  network_admin_intern_acl)

	def tearDown(self):
		self.session.close()
		os.remove(DefaultSetupMixin.DB_PATH)


class ParseYAMLSetupMixin:

	DB_PATH = 'db.sqlite'
	WHOLE_DB_PATH = 'sqlite:///' + DB_PATH
	ACL_CONFIG = 'acl-config.yaml'

	def setUp(self):
		self.session, self.engine = setup_database(ParseYAMLSetupMixin.WHOLE_DB_PATH)
		ACL.setup(self.engine, access_levels_config=ParseYAMLSetupMixin.ACL_CONFIG)

		# create exemplary users
		ACL.Users.add([ACL.UserModel(username='chair1'), ACL.UserModel(username='chair2')],
					  ACL.root_access_level)

		ACL.Users.add([ACL.UserModel(username='trads')],
					  ACL.AccessLevels.get(role_description='Tradesman'))

		ACL.Users.add([ACL.UserModel(username='tradsjun1'), ACL.UserModel(username='tradsjun2')],
					  ACL.AccessLevels.get(role_description='Tradesman Junior'))

		ACL.Users.add([ACL.UserModel(username='account')],
					  ACL.AccessLevels.get(role_description='Accountant'))

		ACL.Users.add([ACL.UserModel(username='accountjun')],
					  ACL.AccessLevels.get(role_description='Accountant Junior'))

		ACL.Users.add([ACL.UserModel(username='accountint')],
					  ACL.AccessLevels.get(role_description='Accountant Intern'))

		ACL.Users.add([ACL.UserModel(username='buyer')],
					  ACL.AccessLevels.get(role_description='Buyer'))

		ACL.Users.add([ACL.UserModel(username='storechief')],
					  ACL.AccessLevels.get(role_description='Storehouse Chief'))


	def tearDown(self):
		self.session.close()
		os.remove(ParseYAMLSetupMixin.DB_PATH)



### DOCKER AND POSTGRES IMAGE REQUIRED ###
# Postgres (or other server-based db engine) is required for testing thread safety - sqlite does not provide concurrency
#
# Postgres is being started in container every time setUp method is called,
# There is also slight delay before proceeding (postgres needs some time to initialize and start listening for connections)
# - not the best way, but the simplest one
#
# After executing test case, when tearDown method is called postgres container is stopped and removed
# 'utils' directory contains bash-scripts for running and stopping postgres,
# note that 'execute' permission might be required:
#
#  $ chmod +x utils/*
#
class PostgresSetupMixin:

	DB_PATH = 'postgresql://postgres:postgres@localhost/postgres'
	ACL_CONFIG = 'acl-config.yaml'

	def setUp(self):
		call('../utils/start_postgres.sh')
		time.sleep(3)
		self.session, self.engine = setup_database(PostgresSetupMixin.DB_PATH)
		ACL.setup(self.engine, access_levels_config=ParseYAMLSetupMixin.ACL_CONFIG)

		# create exemplary users
		ACL.Users.add([ACL.UserModel(username='admin1'), ACL.UserModel(username='admin2')],
					  ACL.root_access_level)
		ACL.Users.add([ACL.UserModel(username='manager1'), ACL.UserModel(username='manager2')],
					  ACL.AccessLevels.get(role_description='Project Manager'))
		ACL.Users.add([ACL.UserModel(username='software-dev1'), ACL.UserModel(username='software-dev2'),
					   ACL.UserModel(username='software-dev3'), ACL.UserModel(username='software-dev4')],
					  ACL.AccessLevels.get(role_description='Software Developer'))
		ACL.Users.add([ACL.UserModel(username='sd-intern1'), ACL.UserModel(username='sd-intern2'),
					   ACL.UserModel(username='sd-intern3'), ACL.UserModel(username='sd-intern4'),
					   ACL.UserModel(username='sd-intern5'), ACL.UserModel(username='sd-intern6')],
					  ACL.AccessLevels.get(role_description='Software Developer Intern'))
		ACL.Users.add([ACL.UserModel(username='network-admin1'), ACL.UserModel(username='network-admin2'),
					   ACL.UserModel(username='network-admin3'), ACL.UserModel(username='network-admin4')],
					  ACL.AccessLevels.get(role_description='Network Admin'))
		ACL.Users.add([ACL.UserModel(username='na-intern1'), ACL.UserModel(username='na-intern2'),
					   ACL.UserModel(username='na-intern3'), ACL.UserModel(username='na-intern4'),
					   ACL.UserModel(username='na-intern5'), ACL.UserModel(username='na-intern6')],
					  ACL.AccessLevels.get(role_description='Network Admin Intern'))

	def tearDown(self):
		self.session.close()
		time.sleep(3)
		call('../utils/clear_postgres.sh')
		# time.sleep(3)
