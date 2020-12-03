from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_acl import ACL
from sqlalchemy_acl.models import UserModel, AccessLevelModel



# engine configuration
engine = create_engine('postgresql://postgres:postgres@localhost/postgres', echo=False)

# model base configuration
Base = declarative_base()

# session configuration and initialization
Session = sessionmaker(bind=engine)
session = Session()


# ACL setup
# engine is required argument
# user_model is optional argument, there is possibility to pass custom user model
# default user model is present in acl.py file
ACL.setup(engine)



# standard model definition
class Wage(Base):
    __tablename__ = 'wages'

    id = Column(Integer, primary_key=True)
    person = Column(String(64), unique=True, nullable=False)
    amount = Column(Integer, unique=False, nullable=False)

    def __repr__(self):
        return '<Wage {0}:{1}:{2}>'.format(self.id, self.person, self.amount)

# creating tables accordingly to model
Base.metadata.create_all(bind=engine)


# main
if __name__ == '__main__':

    # some exemplary db entries - wages, user and acl
    dummy_list = [
        Wage(id=0, person='Prezio', amount=1000000),
    ]
     
    try:
        session.add_all(dummy_list)
        session.commit()
    except IntegrityError as err:
        print('Integrity Error! Rolling back...')
        session.rollback()

    
    # add new AccessLevels
    manager_access_level = AccessLevelModel(role_description='manager')
    ACL.UserInterface.add_access_levels([manager_access_level])

    # add users with different access levels
    admin = UserModel(username='admin69')
    ACL.UserInterface.add_users([admin], ACL.root_access_level)

    manager = UserModel(username='manager2137')
    ACL.UserInterface.add_users([manager], manager_access_level)

    

    # manager adds more users to database
    ACL.set_user(manager)
    dummy_list = [
        Wage(id=1, person='Praktykantka', amount=1000),
        Wage(id=2, person='Programista15k', amount=15000),
        Wage(id=3, person='Programista10k', amount=10000),
    ]

    try:
        session.add_all(dummy_list)
        session.commit()
    except IntegrityError as err:
        print('Integrity Error! Rolling back...')
        session.rollback()


    print(session.query(Wage).all())

    ACL.set_user(admin)
    print(session.query(Wage).all())
    # # setting user that is about to execute query
    # ACL.set_user(admin_user)
    # print(session.query(Wage).all())
    #
    # ACL.set_user(some_user1)
    # print(session.query(Wage).all())
    #
    # ACL.set_user(some_user2)
    # print(session.query(Wage).all())

