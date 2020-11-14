from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from acl import ACL


# engine configuration
engine = create_engine('sqlite:///db.sqlite')

# model base configuration
Base = declarative_base()

# session configuration and initialization
Session = sessionmaker(bind=engine, query_cls=ACL.Query)
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
    list = [
        Wage(id=1, person='Prezio', amount=1000000), 
        Wage(id=2, person='Praktykantka', amount=1000),
        Wage(id=3, person='Programista15k', amount=15000),

        ACL.UserModel(id=1, username='admin'),
        
        ACL.ACLEntry(user_id=1, dest_table='wages', dest_id=2),
        ACL.ACLEntry(user_id=1, dest_table='wages', dest_id=3),        
    ]
    
    
    # standard procedure of commiting changes to db
    # IntegrityError is raised when, for example, new object with same id is creating 
    try:
        session.add_all(list)
        session.commit()
    except IntegrityError as err:
        print('Integrity Error! Rolling back...')
        session.rollback()

    # getting admin user object
    # quering from users table (defined by ACL.UserModel) is not restricted by ACL
    admin_user = session.query(ACL.UserModel).filter_by(id=1).scalar()

    # setting user that is about to execute query
    ACL.set_user(admin_user)

    # actual query, we defined in ACL table tha admin_user have access to wage:2 and wage:3
    wages = session.query(Wage).all()
    print(wages)

