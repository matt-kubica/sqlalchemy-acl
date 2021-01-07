from copy import copy

from .exceptions import ACLModelNotValid, UserNotValid
from .models import UserModel, AccessLevelModel, ACLEntryModel
from .utils import check_users_list, check_entries_list, check_access_levels_list
from .base import DeclarativeBase
from .events import intercept_insert, intercept_select, intercept_delete
from .collections import AccessLevelsTree, AccessLevelsParser

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker


class ACL:

    # class properties
    client_engine = None
    inner_engine = None
    inner_session = None
    current_user = None
    root_access_level = None

    # setting up engine and optionally user_model
    @classmethod
    def setup(cls, engine, access_levels_config=None):

        # creating copy of client's engine
        cls.client_engine = engine
        cls.inner_engine = copy(engine)
        Session = sessionmaker(bind=cls.inner_engine)
        cls.inner_session = Session()

        # create tables accordingly to user model and acl model
        if issubclass(UserModel, DeclarativeBase) and \
           issubclass(ACLEntryModel, DeclarativeBase) and \
           issubclass(AccessLevelModel, DeclarativeBase):
            DeclarativeBase.metadata.create_all(bind=cls.inner_engine)
        else:
            raise ACLModelNotValid

        # access-levels config
        # parse yaml config file or create default root access-level
        if access_levels_config:
            access_levels = AccessLevelsParser(access_levels_config).get_access_levels()
            cls.root_access_level = access_levels[0]
        else:
            cls.root_access_level = AccessLevelModel(role_description='root')
        ACL.AccessLevels.add([cls.root_access_level])

        # attach events
        event.listen(cls.client_engine, 'before_execute', intercept_select, retval=True)
        event.listen(cls.client_engine, 'before_execute', intercept_insert, retval=True)
        event.listen(cls.client_engine, 'before_execute', intercept_delete, retval=True)


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

        # get access level associated with current user
        user_access_level = ACL.inner_session.query(AccessLevelModel) \
                .filter(AccessLevelModel.users.contains(ACL.current_user)) \
                .scalar()

        # get all sub-access-levels
        user_sub_access_levels = AccessLevelsTree(user_access_level).subnodes_list()

        # return all entries of ACLModel accordingly to dest_table and user_sub_access_levels
        filtered_entries = []
        for acl in user_sub_access_levels:
            filtered_entries += cls.inner_session.query(ACLEntryModel) \
            .filter(ACLEntryModel.dest_table == table) \
            .filter(ACLEntryModel.access_levels.contains(acl)) \
            .all()

        return [entry.dest_id for entry in filtered_entries]


    class Users:

        # add new user and attach it to given access_level
        @staticmethod
        def add(users, access_level=None):
            if check_users_list(users):
                ACL.inner_session.add_all(users)
                if access_level:
                    access_level.users.extend(users)
                ACL.inner_session.commit()

        @staticmethod
        def get(**kwargs):
            users = ACL.inner_session.query(UserModel).filter_by(**kwargs).all()
            if len(users) > 1: return users
            elif len(users) == 1: return users[0]
            else: return None

        @staticmethod
        def update(user, **kwargs):
            pass

        @staticmethod
        def delete(user):
            pass


    class AccessLevels:

        @staticmethod
        def add(access_levels):
            if check_access_levels_list(access_levels):
                ACL.inner_session.add_all(access_levels)
                ACL.inner_session.commit()

        @staticmethod
        def get(**kwargs):
            access_levels = ACL.inner_session.query(AccessLevelModel).filter_by(**kwargs).all()
            if len(access_levels) > 1: return access_levels
            elif len(access_levels) == 1: return access_levels[0]
            else: return None

        @staticmethod
        def update(access_level, **kwargs):
            pass

        @staticmethod
        def delete(access_level):
            pass


    class Entries:

        @staticmethod
        def get(**kwargs):
            pass

