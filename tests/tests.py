import sys
import unittest
sys.path.insert(0,'..')

from tests.setup import DefaultSetupMixin, ParseYAMLSetupMixin
from tests.models import ExemplaryModel
from sqlalchemy_acl import ACL
from sqlalchemy_acl.models import UserModel

from random import randrange


class StandardQueriesTestCase(ParseYAMLSetupMixin, unittest.TestCase):

	def test_get_users(self):
		# get all available users, for this setup case
		users = ACL.Users.get()
		self.assertIsInstance(users, list)
		self.assertTrue(users)
		[self.assertIsInstance(user, UserModel) for user in users]


	def test_add_users(self):
		ex_user = UserModel(username='example_user')
		ACL.Users.add([ex_user])
		self.assertEqual(ACL.Users.get(username='example_user'), ex_user)


	def test_get_objects(self):
		# wages associated with root access level
		root_level_objects = [
			ExemplaryModel(id=1, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=2, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=3, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=4, string_field='some_string', integer_field=randrange(100000)),
		]
		self.session.add_all(root_level_objects)
		self.session.commit()

		# user at one of lowest access-levels
		some_user = ACL.Users.get(username='na-intern1')
		other_level_objects = [
			ExemplaryModel(id=5, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=6, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=7, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=8, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=9, string_field='some_string', integer_field=randrange(100000)),
		]
		ACL.set_user(some_user)
		self.session.add_all(other_level_objects)
		self.session.commit()
		ACL.unset_user()

		# set admin user
		ACL.set_user(ACL.Users.get(username='admin1'))
		# check if all added entries are accessible for admin (root access-level user)
		self.assertEqual(self.session.query(ExemplaryModel).all(), root_level_objects + other_level_objects)
		ACL.unset_user()

		# set exemplary user
		ACL.set_user(some_user)
		# check if entries added by exemplary user are accessible for him
		self.assertEqual(self.session.query(ExemplaryModel).all(), other_level_objects)
		ACL.unset_user()

		# set other exemplary user at same access-level
		ACL.set_user(ACL.Users.get(username='na-intern4'))
		self.assertEqual(self.session.query(ExemplaryModel).all(), other_level_objects)
		ACL.unset_user()

		# set other exemplary user at different access-level
		ACL.set_user(ACL.Users.get(username='sd-intern2'))
		# this user shouldn't have access to any entries
		self.assertEqual(self.session.query(ExemplaryModel).all(), [])
		self.assertNotEqual(self.session.query(ExemplaryModel), other_level_objects)
		ACL.unset_user()



if __name__ == '__main__':
	unittest.main()
