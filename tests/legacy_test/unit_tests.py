import sys, unittest
sys.path.insert(0,'../..')
sys.path.insert(1,'..')

from legacy_test.setup import DefaultSetupMixin, ParseYAMLSetupMixin, PostgresSetupMixin
from legacy_test.models import ExemplaryModel
from sqlalchemy_acl import ACL

from random import randrange


class StandardQueriesTestCase(ParseYAMLSetupMixin, unittest.TestCase):

	def test_get_users(self):
		# get all available users, for this setup case
		users = ACL.Users.get()
		self.assertIsInstance(users, list)
		self.assertTrue(users)
		[self.assertIsInstance(user, ACL.user_model) for user in users]


	def test_add_users(self):
		ex_user = ACL.user_model(username='example_user')
		ACL.Users.add([ex_user])
		self.assertEqual(ACL.Users.get(username='example_user'), ex_user)


	def test_get_objects(self):
		# objects associated with root access level
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


	def test_delete_object_with_select(self):
		# objects associated with root access level
		root_level_objects = [
			ExemplaryModel(id=1, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=2, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=3, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=4, string_field='some_string', integer_field=randrange(100000)),
		]
		self.session.add_all(root_level_objects)
		self.session.commit()

		ACL.set_user(ACL.Users.get(username='admin1'))
		# get first object (object with id = 1)
		object = self.session.query(ExemplaryModel).get(1)
		# delete object and commit changes to database
		self.session.delete(object)
		self.session.commit()

		# create set corresponding to initial list without first object
		after_deletion = set(root_level_objects) - {object}
		# assert with select query result
		self.assertEqual(after_deletion, set(self.session.query(ExemplaryModel).all()))
		ACL.unset_user()


	def test_delete_object_without_select(self):
		# objects associated with root access level
		root_level_objects = [
			ExemplaryModel(id=1, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=2, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=3, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=4, string_field='some_string', integer_field=randrange(100000)),
		]
		self.session.add_all(root_level_objects)
		self.session.commit()

		ACL.set_user(ACL.Users.get(username='admin1'))
		# delete object with id = 1
		self.session.query(ExemplaryModel).filter_by(id=1).delete()
		self.session.commit()

		after_deletion = self.session.query(ExemplaryModel).filter(ExemplaryModel.id.in_([2,3,4]))
		self.assertEqual(set(after_deletion), set(self.session.query(ExemplaryModel).all()))
		ACL.unset_user()


### DOCKER AND POSTGRES IMAGE REQUIRED ###
# for more see notes above setup.PostgresSetupMixin class
# if you want to skip this test case, simply comment it out (yes, there is probably better way of doing this ;) )
class StandardConcurrentQueriesTestCase(PostgresSetupMixin, unittest.TestCase):

	def test_parallel_selects(self):
		# objects associated with root access level
		root_level_objects = [
			ExemplaryModel(id=1, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=2, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=3, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=4, string_field='some_string', integer_field=randrange(100000)),
		]
		self.session.add_all(root_level_objects)
		self.session.commit()

		import threading, logging, random
		format = "%(asctime)s: %(message)s"
		logging.basicConfig(format=format, level=logging.DEBUG,
							datefmt="%H:%M:%S")

		def thread_function(id):
			logging.debug('Thread {0} started..'.format(id))
			for _ in range(3):
				ACL.set_user(ACL.Users.get(username='admin1'))
				objects = self.session.query(ExemplaryModel).all()
				logging.debug('thread = {0}, objects = {1}'.format(id, objects))
				self.assertEqual(root_level_objects, objects)
				ACL.unset_user()
			logging.debug('Thread {0} finished..'.format(id))

		threads = []
		for i in range(5):
			thr = threading.Thread(target=thread_function, args=(i,))
			threads.append(thr)
			thr.start()

		for thr in threads:
			thr.join()






if __name__ == '__main__':
	unittest.main()

