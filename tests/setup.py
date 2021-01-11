import sys, os
import time
from subprocess import call
sys.path.insert(0,'..')


from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from sqlalchemy_acl import ACL
from sqlalchemy_acl.models import AccessLevelModel, UserModel

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

		# create exemplary access-levels structure
		director_acl = AccessLevelModel(role_description='Executive Director', parent=ACL.root_access_level)
		project_manager_acl = AccessLevelModel(role_description='Project Manager', parent=director_acl)
		software_developer_acl = AccessLevelModel(role_description='Software Developer', parent=project_manager_acl)
		network_admin_acl = AccessLevelModel(role_description='Network Admin', parent=project_manager_acl)
		devops_acl = AccessLevelModel(role_description='Dev Ops', parent=project_manager_acl)
		software_dev_intern_acl = AccessLevelModel(role_description='Software Developer Intern', parent=software_developer_acl)
		network_admin_intern_acl = AccessLevelModel(role_description='Network Admin Intern', parent=network_admin_acl)

		ACL.AccessLevels.add([director_acl, project_manager_acl, software_developer_acl, network_admin_intern_acl,
							  devops_acl, software_dev_intern_acl, network_admin_intern_acl])

		# create exemplary users
		ACL.Users.add([UserModel(username='admin1'), UserModel(username='admin2')],
					  ACL.root_access_level)
		ACL.Users.add([UserModel(username='manager1'), UserModel(username='manager2')],
					  project_manager_acl)
		ACL.Users.add([UserModel(username='software-dev1'), UserModel(username='software-dev2'),
					   UserModel(username='software-dev3'), UserModel(username='software-dev4')],
					  software_developer_acl)
		ACL.Users.add([UserModel(username='sd-intern1'), UserModel(username='sd-intern2'),
					   UserModel(username='sd-intern3'), UserModel(username='sd-intern4'),
					   UserModel(username='sd-intern5'), UserModel(username='sd-intern6')],
					  software_dev_intern_acl)
		ACL.Users.add([UserModel(username='network-admin1'), UserModel(username='network-admin2'),
					   UserModel(username='network-admin3'), UserModel(username='network-admin4')],
					  network_admin_acl)
		ACL.Users.add([UserModel(username='na-intern1'), UserModel(username='na-intern2'),
					   UserModel(username='na-intern3'), UserModel(username='na-intern4'),
					   UserModel(username='na-intern5'), UserModel(username='na-intern6')],
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
		ACL.setup(self.engine, ParseYAMLSetupMixin.ACL_CONFIG)

		# create exemplary users
		ACL.Users.add([UserModel(username='admin1'), UserModel(username='admin2')],
					  ACL.root_access_level)
		ACL.Users.add([UserModel(username='manager1'), UserModel(username='manager2')],
					  ACL.AccessLevels.get(role_description='Project Manager'))
		ACL.Users.add([UserModel(username='software-dev1'), UserModel(username='software-dev2'),
					   UserModel(username='software-dev3'), UserModel(username='software-dev4')],
					  ACL.AccessLevels.get(role_description='Software Developer'))
		ACL.Users.add([UserModel(username='sd-intern1'), UserModel(username='sd-intern2'),
					   UserModel(username='sd-intern3'), UserModel(username='sd-intern4'),
					   UserModel(username='sd-intern5'), UserModel(username='sd-intern6')],
					  ACL.AccessLevels.get(role_description='Software Developer Intern'))
		ACL.Users.add([UserModel(username='network-admin1'), UserModel(username='network-admin2'),
					   UserModel(username='network-admin3'), UserModel(username='network-admin4')],
					  ACL.AccessLevels.get(role_description='Network Admin'))
		ACL.Users.add([UserModel(username='na-intern1'), UserModel(username='na-intern2'),
					   UserModel(username='na-intern3'), UserModel(username='na-intern4'),
					   UserModel(username='na-intern5'), UserModel(username='na-intern6')],
					  ACL.AccessLevels.get(role_description='Network Admin Intern'))

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
		call('utils/start_postgres.sh')
		time.sleep(3)
		self.session, self.engine = setup_database(PostgresSetupMixin.DB_PATH)
		ACL.setup(self.engine, ParseYAMLSetupMixin.ACL_CONFIG)

		# create exemplary users
		ACL.Users.add([UserModel(username='admin1'), UserModel(username='admin2')],
					  ACL.root_access_level)
		ACL.Users.add([UserModel(username='manager1'), UserModel(username='manager2')],
					  ACL.AccessLevels.get(role_description='Project Manager'))
		ACL.Users.add([UserModel(username='software-dev1'), UserModel(username='software-dev2'),
					   UserModel(username='software-dev3'), UserModel(username='software-dev4')],
					  ACL.AccessLevels.get(role_description='Software Developer'))
		ACL.Users.add([UserModel(username='sd-intern1'), UserModel(username='sd-intern2'),
					   UserModel(username='sd-intern3'), UserModel(username='sd-intern4'),
					   UserModel(username='sd-intern5'), UserModel(username='sd-intern6')],
					  ACL.AccessLevels.get(role_description='Software Developer Intern'))
		ACL.Users.add([UserModel(username='network-admin1'), UserModel(username='network-admin2'),
					   UserModel(username='network-admin3'), UserModel(username='network-admin4')],
					  ACL.AccessLevels.get(role_description='Network Admin'))
		ACL.Users.add([UserModel(username='na-intern1'), UserModel(username='na-intern2'),
					   UserModel(username='na-intern3'), UserModel(username='na-intern4'),
					   UserModel(username='na-intern5'), UserModel(username='na-intern6')],
					  ACL.AccessLevels.get(role_description='Network Admin Intern'))

	def tearDown(self):
		self.session.close()
		time.sleep(3)
		call('utils/clear_postgres.sh')
		# time.sleep(3)