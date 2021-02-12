import os, csv, inspect, sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_acl import ACL
from sqlalchemy_acl.models import AccessLevelModel, ACLEntryModel

from . import models


CSV_DIR = 'flask_test/imports'
DB_PATH = 'db.sqlite'
WHOLE_DB_PATH = 'sqlite:///' + DB_PATH

defined_models = [cls for _, cls in inspect.getmembers(sys.modules[models.__name__], inspect.isclass)]



Base = declarative_base()
engine = create_engine(WHOLE_DB_PATH, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(bind=engine)
ACL.setup(engine)


def import_from_csv(session):
    csv_files = [filename for filename in os.listdir(CSV_DIR) if filename.endswith('.csv')]

    for filename in csv_files:
        tablename = filename.rsplit('.', 1)[0]
        CurrentModel = [m for m in defined_models if m.__tablename__ == tablename][0]

        abs_path = '{0}/{1}/{2}'.format(os.path.abspath('.'), CSV_DIR, filename)
        with open(abs_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=';')


            for row in csv_reader:
                access_levels_list = list(map(int, row[-1].split(',')))
                object_id = row[0]
                properties = row[: -1]
                print(properties)

                for access_level in access_levels_list:
                    user_access_level = ACL.inner_session.query(AccessLevelModel) \
                        .filter(AccessLevelModel.id == access_level) \
                        .scalar()


                    session.add(CurrentModel(*properties))
                    session.commit()


                    entry = ACL.inner_session.query(ACLEntryModel) \
                            .filter(ACLEntryModel.dest_id == object_id and ACLEntryModel.dest_table == tablename) \
                            .scalar()
                    entry.access_levels.append(user_access_level)
                    ACL.inner_session.add(entry)
                    ACL.inner_session.commit()

import_from_csv(session)