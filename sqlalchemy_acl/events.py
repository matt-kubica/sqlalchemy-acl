from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.dml import Insert, Delete

from .models import ACLEntryModel, UserModel, AccessLevelModel


# function for intercepting query statement before execution and applying filter accordingly to user
def intercept_select(conn, clauseelement, multiparams, params):
    from . import ACL

    # check if it's select statement
    if isinstance(clauseelement, Select):
        # 'froms' represents list of tables that statement is querying, for now, let's assume there is only one table
        table = clauseelement.froms[0]

        # adding filter in statement
        clauseelement = clauseelement.where(table.c.id.in_(ACL.allowed_rows(str(table))))

    # because retval flag in hook is set to True, we need to return this tuple of parameters, this is required
    # to apply additional filter
    return clauseelement, multiparams, params


# function for intercepting query
# adds appropriate ACLEntry for given object, attaches newly created ACLEntry to AccessLevel based on ACL.current_user
# if current user is set to None, ACLEntry is attached to root AccessLevel
def intercept_insert(conn, clauseelement, multiparams, params):
    from . import ACL

    # check if it's insert statement
    if isinstance(clauseelement, Insert):
        tablename = str(clauseelement.table)
        # get AccessLevel of user currently set in ACL or 'root_access_level' if no user is set
        if ACL.current_user == None:
            user_access_level = ACL.root_access_level
        else:
            user_access_level = ACL.inner_session.query(AccessLevelModel) \
                .filter(AccessLevelModel.users.contains(ACL.current_user)) \
                .scalar()


        try:
            # iterate over dictionaries with properties of objects
            for object_dict in multiparams[0]:
                id = object_dict['id']
                # create appropriate ACLEntry
                entry = ACLEntryModel(dest_table=tablename, dest_id=id)
                # attach ACLEntry to AccessLevel
                entry.access_levels.append(user_access_level)
                ACL.inner_session.add(entry)

            # add objects to database
            ACL.inner_session.commit()
        except IntegrityError:
            ACL.inner_session.rollback()

    return clauseelement, multiparams, params


# function for intercepting delete statement - adds appropriate filter according to who is deleting
def intercept_delete(conn, clauseelement, multiparams, params):
    from . import ACL

    if isinstance(clauseelement, Delete):
        # 'froms' represents list of tables that statement is querying, for now, let's assume there is only one table
        table = clauseelement.table

        # adding filter in statement
        clauseelement = clauseelement.where(table.c.id.in_(ACL.allowed_rows(str(table))))

        # removing ACLEntry corresponding to given objects
        for object_dict in multiparams[0]:
            id = object_dict['id']
            # print('dest_id = {0}, dest_table = {1}'.format(id, str(table)))
            ACL.inner_session.query(ACLEntryModel).filter_by(dest_id=id, dest_table=str(table)).delete()
            ACL.inner_session.commit()

    return clauseelement, multiparams, params