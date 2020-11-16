# SQLAlchemy Acces List


## Virtual Environment
To initialize virtual env run following command in project root, `pipenv` required
```bash
$ pipenv shell
```


## Testing ACL 
Easiest way to test is creating simple script
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_acl import ACL
from models import Base, Wage


# creating engine and session, creating tables in db according to models
engine = create_engine('sqlite:///db.sqlite')
Session = sessionmaker(bind=engine, query_cls=ACL.Query)
session = Session()
Base.metadata.create_all(bind=engine)

# attchaing engine to ACL, initializing ACL
ACL.setup(engine)

# example entries for db
# defining few wages and two users, and acl
# admin has access to all entries in wages table, while std_user cannot access 'Prezio`
entries = [
    # wages
    Wage(id=1, person='Prezio', amount=1000000),
    Wage(id=2, person='Programista15k', amount=15000),
    Wage(id=3, person='Programista10k', amount=10000),
    Wage(id=4, person='Praktykantka', amount=1000),

    # users
    ACL.UserModel(id=1, username='admin'),
    ACL.UserModel(id=2, username='std_user'),

    # admin access
    ACL.ACLEntry(user_id=1, dest_table='wages', dest_id=1),
    ACL.ACLEntry(user_id=1, dest_table='wages', dest_id=2),
    ACL.ACLEntry(user_id=1, dest_table='wages', dest_id=3),
    ACL.ACLEntry(user_id=1, dest_table='wages', dest_id=4),
    
    # std_user access
    ACL.ACLEntry(user_id=2, dest_table='wages', dest_id=2),
    ACL.ACLEntry(user_id=2, dest_table='wages', dest_id=3),
    ACL.ACLEntry(user_id=2, dest_table='wages', dest_id=4)
]
# adding entries to session and commiting to db
session.add_all(entries)
session.commit()


# retrieving admin and std_user objects
admin = session.query(ACL.UserModel).filter_by(id=1).scalar()
std_user = session.query(ACL.UserModel).filter_by(id=2).scalar()


# when user is not set empty array will be returned
print(session.query(Wage).all())
# []

# setting user before executing query
ACL.set_user(admin)
print(session.query(Wage).all())
# [<Wage 1:Prezio:1000000>, <Wage 2:Programista15k:15000>, <Wage 3:Programista10k:10000>, <Wage 4:Praktykantka:1000>]

# setting user before executing query
ACL.set_user(std_user)
print(session.query(Wage).all())
# [<Wage 2:Programista15k:15000>, <Wage 3:Programista10k:10000>, <Wage 4:Praktykantka:1000>]

# unsetting user
ACL.unset_user()
print(session.query(Wage).all())
# []
```


## ACL.Query
**ACL.Query** can be used with legacy sqlalchemy project as well as with flask_sqlalchemy project. Due to different usage of those two, connecting **ACL** 
may vary, see *legacy_sqlalchemy_test.py* and *flask_sqlalchemy_test.py*.
