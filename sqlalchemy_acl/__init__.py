from .exceptions import UserNotFromUserModel, EngineNotProvided, ACLModelsNotProvided

from sqlalchemy.orm.query import Query as BaseQuery
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import UniqueConstraint



class ACL:

    # Query class that appends filter to every query
    class Query(BaseQuery):
        
        def get(self, ident):
            # Override get() so that the flag is always checked in the
            # DB as opposed to pulling from the identity map. - this is optional.
            return BaseQuery.get(self.populate_existing(), ident)

        def __iter__(self):
            return BaseQuery.__iter__(self.private())

        def from_self(self, *ent):
            # Override from_self() to automatically apply
            # the criterion to.  this works with count() and
            # others.
            return BaseQuery.from_self(self.private(), *ent)

        def private(self):
            mzero = self._mapper_zero()
            
            if mzero:
                # get model class
                Model = mzero.class_

                # actually appending filter here
                # checking if object id is in the ACL list for given object
                return self.enable_assertions(False).filter(Model.id.in_(ACL.create_acl(Model)))
            return self


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


    # class properties
    UserModel = User
    ACLModel = ACLEntry
    Session = None
    engine = None
    user_id = None
    

    # seting up engine and optionally user_model
    @classmethod
    def setup(cls, engine, user_model=None):

        # checking if engine is provided (needs to be!)
        if not engine:
            raise EngineNotProvided

        # session configuration
        cls.Session = sessionmaker(bind=engine)
        cls.engine = engine

        # if no custom user model is given, use default
        if user_model is not None:
            cls.UserModel = user_model

        # create tables acordingly to user model and acl model
        if cls.UserModel and cls.ACLModel:
            cls.Base.metadata.create_all(bind=engine)
        else:
            raise ACLModelsNotProvided


    @classmethod
    def set_user(cls, user):
        # checking if given model is instance of UserModel
        if isinstance(user, cls.UserModel):
            cls.user_id = user.id
        else:
            raise UserNotFromUserModel

    @classmethod
    def unset_user(cls):
        if cls.user_id is not None:
            cls.user_id = None


    # creating list of available entries for requesting user acording to requesting model
    @classmethod
    def create_acl(cls, model):
        session = cls.Session()

        # returning full list of ids if user model is requested
        # by default everybody have acces to users table
        if model == cls.UserModel:
            users = session.query(cls.UserModel).all()
            return [user.id for user in users]

        # if user is not specified, return empty list
        if cls.user_id is None:
            return []
        

        # get all entries for acl acording to dest_table and user_id
        acls = session.query(cls.ACLModel) \
            .filter(cls.ACLModel.dest_table == model.__tablename__) \
            .filter(cls.ACLModel.user_id == cls.user_id) \
            .all()
        
        # retrieve only ids
        return [entry.dest_id for entry in acls]
        
        
