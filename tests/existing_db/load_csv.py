import sys
import os

sys.path.insert(0,'../..')
sys.path.insert(1,'..')

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_acl import ACL
from sqlalchemy_acl.models import AccessLevelModel, ACLEntryModel

import csv
import re

"""
def determine_dtypes(csv_reader):
    dtypes_list = []
    first_row = next(csv_reader)

    for cell in first_row:
        if re.search('^-?(\d)+$', cell):
            print('INTEGER FOUND')
            dtypes_list.append(lambda x: int(x))
        elif re.search('^-?(\d)+.(\d)+$', cell):
            print('FLOAT FOUND')
            dtypes_list.append(lambda x: float(x))
        else:
            print('DATE OR STRING FOUND')
"""

Base = declarative_base()

def setup_database(db_path):
	engine = create_engine(db_path, echo=False)
	Session = sessionmaker(bind=engine)
	session = Session()
	Base.metadata.create_all(bind=engine)
	return session, engine

class ParseYAMLSetupMixin:

    DB_PATH = 'db.sqlite'
    WHOLE_DB_PATH = 'sqlite:///' + DB_PATH
    ACL_CONFIG = 'acl-config.yaml'

    def setUp(self):
    	self.session, self.engine = setup_database(ParseYAMLSetupMixin.WHOLE_DB_PATH)
    	ACL.setup(self.engine, access_levels_config=ParseYAMLSetupMixin.ACL_CONFIG)

    	ACL.Users.add([ACL.UserModel(username='chair')], ACL.root_access_level)
    	ACL.Users.add([ACL.UserModel(username='account')], ACL.AccessLevels.get(role_description='Accountant'))
    	ACL.Users.add([ACL.UserModel(username='trads')], ACL.AccessLevels.get(role_description='Tradesman'))

    def tearDown(self):
    	self.session.close()
    	os.remove(ParseYAMLSetupMixin.DB_PATH)

    def getACLFromFiles(self):
        filenames = os.listdir('.')
        csv_files = [filename for filename in filenames if filename.endswith('.csv')]

        for f in csv_files:
            with open(f, 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=';')
                tablename = f[:-4]

                for row in csv_reader:
                    access_levels_list = list(map(int, row[-1].split(',')))
                    row_id = row[0]

                    for access_level in access_levels_list:
                        user_access_level = ACL.inner_session.query(AccessLevelModel) \
                            .filter(AccessLevelModel.id == access_level) \
                            .scalar()

                        # print(f'PRINTUJECSV {user_access_level}')

                        entry = ACLEntryModel(dest_table=tablename, dest_id=row_id)
                        entry.access_levels.append(user_access_level)
                        ACL.inner_session.add(entry)

main_obj = ParseYAMLSetupMixin()
main_obj.setUp()
main_obj.getACLFromFiles()
main_obj.tearDown()
