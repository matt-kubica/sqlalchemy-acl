from copy import copy

from .exceptions import UserNotValid, ACLModelsNotValid, ListRequired, ACLEntryNotValid

from sqlalchemy import event
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import UniqueConstraint


# model base configuration
Base = declarative_base()

# default user model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)

    def __repr__(self):
        return '<User {0}:{1}>'.format(self.id, self.username)


# ACLEntry model
class ACLEntry(Base):
    __tablename__ = 'acl'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    dest_table = Column(String(64), nullable=False)
    dest_id = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'dest_table', 'dest_id'),)

    def __repr__(self):
        return '<ACLEntry {0}:{1} -> {2}:{3}>'.format(
            self.id,
            self.user_id,
            self.dest_table,
            self.dest_id
        )



class ACL:

    # class properties
    UserModel = User
    ACLModel = ACLEntry
    client_engine = None
    inner_engine = None
    InnerSession = None
    user_id = None

    # setting up engine and optionally user_model
    @classmethod
    def setup(cls, engine, user_model=None):

        # if no custom user model is given, use default
        if user_model is not None:
            cls.UserModel = user_model

        # creating copy of client's engine
        cls.client_engine = engine
        cls.inner_engine = copy(engine)
        cls.InnerSession = sessionmaker(bind=cls.inner_engine)

        # create tables accordingly to user model and acl model
        if issubclass(cls.UserModel, Base) and issubclass(cls.ACLModel, Base):
            Base.metadata.create_all(bind=cls.inner_engine)
        else:
            raise ACLModelsNotValid

        #
        event.listen(cls.client_engine, 'before_execute', ACL.intercept, retval=True)

    @classmethod
    def set_user(cls, user):
        # checking if given model is instance of UserModel
        if isinstance(user, cls.UserModel):
            cls.user_id = user.id
        else:
            raise UserNotValid

    @classmethod
    def unset_user(cls):
        if cls.user_id is not None:
            cls.user_id = None

    # function for intercepting query statement before execution and applying filter acordingly to user
    @staticmethod
    def intercept(conn, clauseelement, multiparams, params):
        from sqlalchemy.sql.selectable import Select

        # check if it's select statement
        if isinstance(clauseelement, Select):
            # 'froms' represents list of tables that statement is querying, for now, let's assume there is only one table
            table = clauseelement.froms[0]

            # adding filter in statement
            clauseelement = clauseelement.where(table.c.id.in_(ACL.allowed_rows(str(table))))

        # because retval flag in hook is set to True, we need to return this tuple of parameters, this is required
        # to apply additional filter
        return clauseelement, multiparams, params

    # creating list of available entries for requesting user accordingly to requested table
    @classmethod
    def allowed_rows(cls, table):
        # creating session object
        session = cls.InnerSession()

        # if user is not specified, return empty list
        if cls.user_id is None:
            return []

        # return all entries of ACLModel accordingly to dest_table and user_id
        filtered_entries = session.query(cls.ACLModel) \
            .filter(cls.ACLModel.dest_table == table) \
            .filter(cls.ACLModel.user_id == cls.user_id) \
            .all()

        return [entry.dest_id for entry in filtered_entries]

    # adding user to DB, raises IntegrityError and UserNotValid
    @staticmethod
    def add_user(user):

        # checking if user model is valid
        if not isinstance(user, ACL.UserModel):
            raise UserNotValid

        session = ACL.InnerSession()
        session.add(user)
        session.commit()

    # adding multiple users to DB at once, raises IntegrityError, ListRequired and UserNotValid
    @staticmethod
    def add_users(users):
        # checking if users is list
        if not isinstance(users, list):
            raise ListRequired

        # checking if every object in list is valid
        if not all([isinstance(user, ACL.UserModel) for user in users]):
            raise UserNotValid

        session = ACL.InnerSession()
        session.add_all(users)
        session.commit()

    @staticmethod
    def delete_user(user):
        pass

    # raises ACLEntryNotValid and IntegrityError
    @staticmethod
    def add_entry(entry):
        # checking if user model is valid
        if not isinstance(entry, ACL.ACLModel):
            raise ACLEntryNotValid

        session = ACL.InnerSession()
        session.add(entry)
        session.commit()

    # raises ACLEntryNotValid, ListRequired and IntegrityError
    @staticmethod
    def add_entries(entries):
        # checking if users is list
        if not isinstance(entries, list):
            raise ListRequired

        # checking if every object in list is valid
        if not all([isinstance(entry, ACL.ACLModel) for entry in entries]):
            raise ACLEntryNotValid

        session = ACL.InnerSession()
        session.add_all(entries)
        session.commit()
