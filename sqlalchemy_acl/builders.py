from abc import ABC, abstractmethod
from .models import AccessLevelModel
from .utils import check_access_levels_list, check_users_list, check_entries_list


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