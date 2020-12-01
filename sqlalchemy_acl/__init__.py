from copy import copy

from .exceptions import ACLModelsNotValid, UserNotValid
from .models import UserModel, AccessLevelModel, ACLEntryModel
from .utils import check_users_list, check_entries_list, check_access_levels_list
from .base import Base
from .events import intercept_select, intercept_insert

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker



class AccessLevelBuilder():

    # raises ListRequired, ACLEntryNotValid, UserNotValid
    def __init__(self, acl_entries=None, users=None):
        if users is None:
            self.users = []
        elif check_users_list(users):
            self.users = users

        if acl_entries is None:
            self.acl_entries = []
        elif check_entries_list(acl_entries):
            self.acl_entries = acl_entries

    # raises ListRequired, ACLEntryNotValid
    def add_alc_entries(self, acl_entries):
        if check_entries_list(acl_entries): self.acl_entries.extend(acl_entries)

    # raises ListRequired, UserNotValid
    def add_users(self, users):
        if check_users_list(users): self.users.extend(users)

    # raises IntegrityError
    def build(self, description=None):
        return AccessLevelModel(users=self.users, entries=self.acl_entries, role_description=description)





class ACL:

    # class properties
    client_engine = None
    inner_engine = None
    inner_session = None
    current_user = None
    root_access_level = None

    # setting up engine and optionally user_model
    @classmethod
    def setup(cls, engine):

        # creating copy of client's engine
        cls.client_engine = engine
        cls.inner_engine = copy(engine)
        Session = sessionmaker(bind=cls.inner_engine)
        cls.inner_session = Session()

        # create tables accordingly to user model and acl model
        if issubclass(UserModel, Base) and issubclass(ACLEntryModel, Base) and issubclass(AccessLevelModel, Base):
            Base.metadata.create_all(bind=cls.inner_engine)
        else:
            raise ACLModelsNotValid

        cls.root_access_level = AccessLevelModel(role_description='superuser')
        cls.inner_session.add(cls.root_access_level)
        cls.inner_session.commit()

        event.listen(cls.client_engine, 'before_execute', intercept_select, retval=True)
        event.listen(cls.client_engine, 'before_execute', intercept_insert, retval=True)



    @classmethod
    def set_user(cls, user):
        # checking if given model is instance of UserModel
        if isinstance(user, UserModel):
            cls.current_user = user
        else:
            raise UserNotValid

    @classmethod
    def unset_user(cls):
        if cls.current_user is not None:
            cls.current_user = None



    # creating list of available entries for requesting user accordingly to requested table
    @classmethod
    def allowed_rows(cls, table):

        # if user is not specified, return empty list
        if cls.current_user is None:
            return []

        user_access_level = ACL.inner_session.query(AccessLevelModel) \
                .filter(AccessLevelModel.users.contains(ACL.current_user)) \
                .scalar()

        # return all entries of ACLModel accordingly to dest_table and user_id
        filtered_entries = cls.inner_session.query(ACLEntryModel) \
            .filter(ACLEntryModel.dest_table == table) \
            .filter(ACLEntryModel.access_levels.contains(user_access_level)) \
            .all()

        return [entry.dest_id for entry in filtered_entries]


    # add new user and attach it to given access_level
    @staticmethod
    def add_users(users, access_level):
        if check_users_list(users):
            ACL.inner_session.add_all(users)
            access_level.users.extend(users)
            ACL.inner_session.commit()

    @staticmethod
    def get_users(**kwargs):
        ACL.inner_session.query(UserModel).filter_by(**kwargs).all()

    @staticmethod
    def update_user(user, **kwargs):
        pass

    @staticmethod
    def delete_user(user):
        pass

    @staticmethod
    def add_access_levels(access_levels):
        if check_access_levels_list(access_levels):
            ACL.inner_session.add_all(access_levels)
            ACL.inner_session.commit()

    # @staticmethod
    # def add_entry(entry):
    #     # checking if user model is valid
    #     if not isinstance(entry, ACL.ACLModel):
    #         raise ACLEntryNotValid
    #
    #     session = ACL.InnerSession()
    #     session.add(entry)
    #     session.commit()
    #
    # # raises ACLEntryNotValid, ListRequired and IntegrityError
    # @staticmethod
    # def add_entries(entries):
    #     # checking if users is list
    #     if not isinstance(entries, list):
    #         raise ListRequired
    #
    #     # checking if every object in list is valid
    #     if not all([isinstance(entry, ACL.ACLModel) for entry in entries]):
    #         raise ACLEntryNotValid
    #
    #     session = ACL.InnerSession()
    #     session.add_all(entries)
    #     session.commit()
