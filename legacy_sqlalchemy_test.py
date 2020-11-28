from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_acl import ACL



# engine configuration
engine = create_engine('sqlite:///db.sqlite')

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
        Wage(id=1, person='Praktykantka', amount=1000),
        Wage(id=2, person='Programista15k', amount=15000),
        Wage(id=3, person='Programista10k', amount=10000),
    ]
    
    
    # standard procedure of commiting changes to db
    # IntegrityError is raised when, for example, new object with same id is creating 
    try:
        session.add_all(dummy_list)
        session.commit()
    except IntegrityError as err:
        print('Integrity Error! Rolling back...')
        session.rollback()

    # adding some exemplary users
    admin_user = ACL.UserModel(id=0, username='admin')
    some_user1 = ACL.UserModel(id=1, username='some_user1')
    some_user2 = ACL.UserModel(id=2, username='some_user2')
    ACL.add_users([admin_user, some_user1, some_user2])

    # adding some exemplary ACL entries
    # admin has access to all rows of 'wages', some_user1 to rows 1..3 and some_user2 to row 3 only
    acl_entries = [
        ACL.ACLModel(id=0, user_id=admin_user.id, dest_table=Wage.__tablename__, dest_id=0),
        ACL.ACLModel(id=1, user_id=admin_user.id, dest_table=Wage.__tablename__, dest_id=1),
        ACL.ACLModel(id=2, user_id=admin_user.id, dest_table=Wage.__tablename__, dest_id=2),
        ACL.ACLModel(id=3, user_id=admin_user.id, dest_table=Wage.__tablename__, dest_id=3),

        ACL.ACLModel(id=4, user_id=some_user1.id, dest_table=Wage.__tablename__, dest_id=1),
        ACL.ACLModel(id=5, user_id=some_user1.id, dest_table=Wage.__tablename__, dest_id=2),
        ACL.ACLModel(id=6, user_id=some_user1.id, dest_table=Wage.__tablename__, dest_id=3),

        ACL.ACLModel(id=7, user_id=some_user2.id, dest_table=Wage.__tablename__, dest_id=3),
    ]
    ACL.add_entries(acl_entries)


    # setting user that is about to execute query
    ACL.set_user(admin_user)
    print(session.query(Wage).all())

    ACL.set_user(some_user1)
    print(session.query(Wage).all())

    ACL.set_user(some_user2)
    print(session.query(Wage).all())

