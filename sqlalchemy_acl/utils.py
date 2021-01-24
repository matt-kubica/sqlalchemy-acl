from .models import UserModelMixin, AccessLevelModel, ACLEntryModel
from .exceptions import UserNotValid, ACLModelNotValid, ListRequired, ACLEntryNotValid, AccessLevelNotValid




def check_users_list(users):
    # checking if passed object is list
    if not isinstance(users, list):
         raise ListRequired

    # checking if every object in list is valid
    if not all([isinstance(user, UserModelMixin) for user in users]):
         raise UserNotValid

    return True


def check_entries_list(entries):
    # checking if passed object is list
    if not isinstance(entries, list):
        raise ListRequired

    # checking if every object in list is valid
    if not all([isinstance(entry, ACLEntryModel) for entry in entries]):
        raise ACLEntryNotValid

    return True


def check_access_levels_list(access_levels):
    # checking if passed object is list
    if not isinstance(access_levels, list):
        raise ListRequired

    # checking if every object in list is valid
    if not all([isinstance(access_level, AccessLevelModel) for access_level in access_levels]):
        raise AccessLevelNotValid

    return True