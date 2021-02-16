import os, csv, inspect, sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from sqlalchemy_acl import ACL
from sqlalchemy_acl.models import AccessLevelModel, ACLEntryModel

from . import models


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, 'imports')
DB_PATH = os.path.join(BASE_DIR, 'db.sqlite')
DB_URI = 'sqlite:///' + DB_PATH


from .models import UpdateMixin
defined_models = set([cls for _, cls in inspect.getmembers(sys.modules[models.__name__], inspect.isclass)]) - {UpdateMixin}



def import_from_csv(session):
    csv_files = [filename for filename in os.listdir(CSV_DIR) if filename.endswith('.csv')]
    print(' * Importing objects from csv files: {0}\n'.format(csv_files))

    for filename in csv_files:
        print(' * Currently processing: {0}'.format(filename))
        tablename = filename.rsplit('.', 1)[0]
        try:
            CurrentModel = [m for m in defined_models if m.__tablename__ == tablename][0]
        except IndexError: continue
        print(' * Found model: {0}'.format(CurrentModel))

        path = os.path.join(CSV_DIR, filename)
        with open(path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=';')

            for row in csv_reader:
                access_levels = list(map(int, row[-1].split(',')))
                object_id = row[0]
                properties = row[: -1]
                print('\tObject properties: {0}'.format(properties))
                print('\tAccess levels list: {0}\n'.format(access_levels))


                session.add(CurrentModel(*properties))
                session.commit()

                entry = ACL.inner_session.query(ACLEntryModel) \
                                         .filter(ACLEntryModel.dest_id == object_id and ACLEntryModel.dest_table == tablename) \
                                         .all()[0]
                entry.access_levels.extend(ACL.inner_session.query(AccessLevelModel)
                                           .filter(AccessLevelModel.id.in_(access_levels)).all())
                ACL.inner_session.add(entry)
                ACL.inner_session.commit()


if __name__ == '__main__':
    Base = declarative_base()
    engine = create_engine(DB_URI, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    if not database_exists(engine.url):
        Base.metadata.create_all(bind=engine)
        create_database(engine.url)

    from .models import UserModel
    ACL.setup(engine, UserModel, 'acl-config.yam;')
    import_from_csv(session)
