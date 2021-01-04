import sys
import unittest
sys.path.insert(0,'..')

from tests.setup import SetupMixin, Wage
from sqlalchemy_acl import ACL
from sqlalchemy_acl.models import UserModel

from random import randrange


class StandardQueriesTestCase(SetupMixin, unittest.TestCase):

	def test_get_users(self):
		# get all available users, for this setup case
		users = ACL.Users.get()
		self.assertIsInstance(users, list)
		self.assertTrue(users)
		[self.assertIsInstance(user, UserModel) for user in users]


	def test_add_users(self):
		ex_user = UserModel(username='example_user')
		ACL.Users.add([ex_user])
		self.assertEqual(ACL.Users.get(username='example_user')[0], ex_user)


	def test_get_wages(self):
		# wages associated with root access level
		root_wages = [
			Wage(id=1, person='wage1', amount=randrange(100000)),
			Wage(id=2, person='wage2', amount=randrange(100000)),
			Wage(id=3, person='wage3', amount=randrange(100000)),
			Wage(id=4, person='wage4', amount=randrange(100000)),
		]
		self.session.add_all(root_wages)
		self.session.commit()

		# user at one of lowest access-levels
		some_user = ACL.Users.get(username='na-intern1')[0]
		other_wages = [
			Wage(id=5, person='wage5', amount=randrange(100000)),
			Wage(id=6, person='wage6', amount=randrange(100000)),
			Wage(id=7, person='wage7', amount=randrange(100000)),
			Wage(id=8, person='wage8', amount=randrange(100000)),
			Wage(id=9, person='wage9', amount=randrange(100000)),
		]
		ACL.set_user(some_user)
		self.session.add_all(other_wages)
		self.session.commit()
		ACL.unset_user()

		# set admin user

		ACL.set_user(ACL.Users.get(username='admin1')[0])
		# check if all added entries are accessible for admin (root access-level user)
		self.assertEqual(self.session.query(Wage).all(), root_wages + other_wages)
		ACL.unset_user()


		# set exemplary user
		ACL.set_user(some_user)
		# check if entries added by exemplary user are accessible for him
		self.assertEqual(self.session.query(Wage).all(), other_wages)
		ACL.unset_user()

		# set other exemplary user at same access-level
		ACL.set_user(ACL.Users.get(username='na-intern4')[0])
		self.assertEqual(self.session.query(Wage).all(), other_wages)
		ACL.unset_user()

		# set other exemplary user at different access-level
		ACL.set_user(ACL.Users.get(username='sd-intern2')[0])
		# this user shouldn't have access to any entries
		self.assertEqual(self.session.query(Wage).all(), [])
		self.assertNotEqual(self.session.query(Wage), other_wages)
		ACL.unset_user()



if __name__ == '__main__':
	unittest.main()
