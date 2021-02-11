# Problemy:
# nie działa wszystko, co potrzebuje JOINa (o ile dobrze rozumiem, to jest problem ze sprawdzaniem acl dla wielu tabel);
# przy update ACL nie ma znaczenia, a chyba powinno mieć

# Trzeba dołożyć:
# czytanie ACL z pliku (żeby móc używać w ramach już istniejącej bazy);
# możliwość przyznania dostępu wybranym użytkownikom niżej w hierarchii
# (np. żeby księgowa mogła ustalić, że rekordy, które dodaje są również widoczne dla stażystki)

import sys, unittest
sys.path.insert(0,'../..')
sys.path.insert(1,'..')

from legacy_test.setup import DefaultSetupMixin, ParseYAMLSetupMixin, PostgresSetupMixin
from legacy_test.models import ExemplaryModel, CustomersModel, OrdersModel
from sqlalchemy_acl import ACL
from sqlalchemy import func

from random import randrange


class StandardQueriesTestCase(ParseYAMLSetupMixin, unittest.TestCase):

	def test_get_users(self):
		# get all available users, for this setup case
		users = ACL.Users.get()
		self.assertIsInstance(users, list)
		self.assertTrue(users)
		[self.assertIsInstance(user, ACL.UserModel) for user in users]

	def test_add_users(self):
		ex_user = ACL.UserModel(username='example_user')
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
		some_user = ACL.Users.get(username='tradsjun1')
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
		ACL.set_user(ACL.Users.get(username='chair2'))
		# check if all added entries are accessible for admin (root access-level user)
		self.assertEqual(self.session.query(ExemplaryModel).all(), root_level_objects + other_level_objects)
		ACL.unset_user()

		# set exemplary user
		ACL.set_user(some_user)
		# check if entries added by exemplary user are accessible for him
		self.assertEqual(self.session.query(ExemplaryModel).all(), other_level_objects)
		ACL.unset_user()

		# set other exemplary user at same access-level
		ACL.set_user(ACL.Users.get(username='tradsjun2'))
		self.assertEqual(self.session.query(ExemplaryModel).all(), other_level_objects)
		ACL.unset_user()

		# set other exemplary user at different access-level
		ACL.set_user(ACL.Users.get(username='accountint'))
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

		ACL.set_user(ACL.Users.get(username='chair1'))
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

		ACL.set_user(ACL.Users.get(username='chair1'))
		# delete object with id = 1
		self.session.query(ExemplaryModel).filter_by(id=1).delete()
		self.session.commit()

		after_deletion = self.session.query(ExemplaryModel).filter(ExemplaryModel.id.in_([2,3,4]))
		self.assertEqual(set(after_deletion), set(self.session.query(ExemplaryModel).all()))
		ACL.unset_user()


	# DELETE, użytkownik wyżej usuwa rekordy stworzone przez użytkownika niżej
	def test_authorized_delete(self):
		ACL.set_user(ACL.Users.get(username='tradsjun2'))

		low_level_objects = [
			ExemplaryModel(id=1, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=2, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=3, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=4, string_field='some_string', integer_field=randrange(100000)),
		]
		self.session.add_all(low_level_objects)
		self.session.commit()

		ACL.set_user(ACL.Users.get(username='chair1'))
		object = self.session.query(ExemplaryModel).first()
		self.session.delete(object)
		self.session.commit()

		ACL.unset_user()
		ACL.set_user(ACL.Users.get(username='tradsjun1'))

		self.assertEqual(self.session.query(ExemplaryModel).all(), low_level_objects[1:])
		ACL.unset_user()


	# WHERE
	def test_filter(self):
		root_level_objects = [
			ExemplaryModel(id=1, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=2, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=3, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=4, string_field='some_string', integer_field=randrange(100000)),
		]
		self.session.add_all(root_level_objects)
		self.session.commit()

		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		low_level_objects = [
			ExemplaryModel(id=5, string_field='some_string', integer_field=randrange(100000)),
			ExemplaryModel(id=6, string_field='some_string', integer_field=randrange(100000))
		]
		self.session.add_all(low_level_objects)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='tradsjun2'))
		self.assertEqual(self.session.query(ExemplaryModel).filter(ExemplaryModel.id > 2).all(), low_level_objects)
		ACL.unset_user()


	# JOIN na tabelach stworzonych przez użytkowników na tym samym poziomie
	def test_same_lvl_join(self):
		ACL.set_user(ACL.Users.get(username='chair1'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='chair2'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998'),
			OrdersModel(id=5, customer_id=3, order_date='08-28-1998') # dla zmyły
		]
		self.session.add_all(orders)
		self.session.commit()

		join = [(customers[0], orders[0]), (customers[0], orders[1]), (customers[1], orders[2]), (customers[1], orders[3])]

		result = self.session.query(CustomersModel, OrdersModel).join(OrdersModel,
								 	CustomersModel.id==OrdersModel.customer_id).all()
		self.assertEqual(result, join)
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='chair1'))
		result = self.session.query(CustomersModel, OrdersModel).join(OrdersModel,
									CustomersModel.id==OrdersModel.customer_id).all()
		self.assertEqual(result, join)
		ACL.unset_user()


	# JOIN z tabelą stworzoną przez użytkownika niżej
	def test_low_lvl_join(self):
		ACL.set_user(ACL.Users.get(username='account'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='accountjun'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998'),
			OrdersModel(id=5, customer_id=3, order_date='08-28-1998') # dla zmyły
		]
		self.session.add_all(orders)
		self.session.commit()

		ACL.set_user(ACL.Users.get(username='account'))
		join = [(customers[0], orders[0]), (customers[0], orders[1]), (customers[1], orders[2]), (customers[1], orders[3])]

		result = self.session.query(CustomersModel, OrdersModel).join(OrdersModel,
								 	CustomersModel.id==OrdersModel.customer_id).all()
		self.assertEqual(result, join)
		ACL.unset_user()


	# JOIN z tabelą stworzoną przez użytkownika wyżej
	def test_high_lvl_join(self):
		ACL.set_user(ACL.Users.get(username='account'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='accountjun'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998'),
			OrdersModel(id=5, customer_id=3, order_date='08-28-1998') # dla zmyły
		]
		self.session.add_all(orders)
		self.session.commit()

		result = self.session.query(CustomersModel.name,
		                        OrdersModel.id, OrdersModel.order_date).join(OrdersModel).all()
		self.assertEqual(result, [])
		ACL.unset_user()


	# JOIN z tabelą stworzoną przez użytkownika wyżej, ale z dodanymi rekordami przez użytkownika niżej
	def test_high_lvl_join(self):
		ACL.set_user(ACL.Users.get(username='account'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='accountjun'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998'),
			OrdersModel(id=5, customer_id=3, order_date='08-28-1998')
		]
		self.session.add_all(orders)
		self.session.commit()

		client = CustomersModel(id=3, name='James Bond', phone_number='007')
		self.session.add(client)
		self.session.commit()

		result = self.session.query(CustomersModel, OrdersModel).join(OrdersModel,
								 	CustomersModel.id==OrdersModel.customer_id).all()
		self.assertEqual(result, [(client, orders[4])])
		ACL.unset_user()


	# UPDATE na rekordzie o wyższym poziomie
	def test_high_lvl_update(self):
		ACL.set_user(ACL.Users.get(username='account'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='accountjun'))
		self.session.query(CustomersModel).filter(CustomersModel.id == 1).update({'name': 'Smill With'})
		self.session.commit()

		ACL.set_user(ACL.Users.get(username='account'))
		result = self.session.query(CustomersModel).first()
		self.assertEqual(result.name, 'Smill With')
		ACL.unset_user()


	# UPDATE na rekordzie o niższym poziomie
	def test_low_lvl_update(self):
		ACL.set_user(ACL.Users.get(username='accountjun'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='account'))
		self.session.query(CustomersModel).filter(CustomersModel.id == 1).update({'name': 'Smill With'})
		self.session.commit()

		result = self.session.query(CustomersModel).first()
		self.assertEqual(result.name, 'Smill With')
		ACL.unset_user()


	# UPDATE na rekordzie o tym samym poziomie, stworzonym przez innego użytkownika
	def test_same_lvl_update(self):
		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='tradsjun2'))
		self.session.query(CustomersModel).filter(CustomersModel.id == 1).update({'name': 'Smill With'})
		self.session.commit()

		result = self.session.query(CustomersModel).first()
		self.assertEqual(result.name, 'Smill With')
		ACL.unset_user()


	# COUNT na rekordach o wyższym poziomie
	def test_high_lvl_aggr(self):
		ACL.set_user(ACL.Users.get(username='accountint'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998')
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='account'))
		orders = [
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998'),
			OrdersModel(id=5, customer_id=3, order_date='08-28-1998')
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='accountint'))
		self.assertEqual(self.session.query(func.count(OrdersModel.id)).scalar(), 2)
		ACL.unset_user()


	# COUNT na rekordach o niższym poziomie
	def test_low_lvl_aggr(self):
		ACL.set_user(ACL.Users.get(username='accountint'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998')
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='account'))
		orders = [
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998'),
			OrdersModel(id=5, customer_id=3, order_date='08-28-1998')
		]
		self.session.add_all(orders)
		self.session.commit()

		self.assertEqual(self.session.query(func.count(OrdersModel.id)).scalar(), 5)
		ACL.unset_user()


	# COUNT na rekordach o tym samym poziomie
	def test_same_lvl_aggr(self):
		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998'),
			OrdersModel(id=5, customer_id=3, order_date='08-28-1998')
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='tradsjun2'))
		self.assertEqual(self.session.query(func.count(OrdersModel.id)).scalar(), 5)
		ACL.unset_user()


	# GROUP BY na rekordach na wyższym poziomie
	def test_high_lvl_groupby(self):
		ACL.set_user(ACL.Users.get(username='account'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='accountjun'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998'),
			OrdersModel(id=5, customer_id=2, order_date='08-28-1998')
		]
		self.session.add_all(orders)
		self.session.commit()

		result = self.session.query(CustomersModel.id, func.count(CustomersModel.id)).join(OrdersModel,
		            CustomersModel.id==OrdersModel.customer_id).group_by(CustomersModel.id).all()
		self.assertEqual(result, [])
		ACL.unset_user()


	# GROUP BY na rekordach na niższym poziomie
	def test_low_lvl_groupby(self):
		ACL.set_user(ACL.Users.get(username='accountjun'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='account'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998'),
			OrdersModel(id=5, customer_id=2, order_date='08-28-1998')
		]
		self.session.add_all(orders)
		self.session.commit()

		result = self.session.query(CustomersModel.id, func.count(CustomersModel.id)) \
					.join(OrdersModel, CustomersModel.id == OrdersModel.customer_id) \
					.group_by(CustomersModel.id).all()
		self.assertEqual(result, [(1, 2), (2, 3)])
		ACL.unset_user()


	# GROUP By na rekordach na tym samym poziomie
	def test_same_lvl_groupby(self):
		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='tradsjun2'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998'),
			OrdersModel(id=5, customer_id=2, order_date='08-28-1998')
		]
		self.session.add_all(orders)
		self.session.commit()

		result = self.session.query(CustomersModel.id, func.count(CustomersModel.id)).join(OrdersModel,
		            CustomersModel.id==OrdersModel.customer_id).group_by(CustomersModel.id).all()
		self.assertEqual(result, [(1, 2), (2, 3)])
		ACL.unset_user()


	# SUBQUERY w JOIN, wyższy powinien widzieć późniejsze daty dodane przez niższego
	def test_low_lvl_subquery(self):
		ACL.set_user(ACL.Users.get(username='trads'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()

		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998')
		]

		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		orders = [
			OrdersModel(id=5, customer_id=1, order_date='10-31-1998'),
			OrdersModel(id=6, customer_id=2, order_date='10-15-1998'),
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='trads'))
		subquery = self.session.query(OrdersModel.customer_id, func.max(OrdersModel.order_date).label('latest_order')
		                        ).group_by(OrdersModel.customer_id).subquery()
		query = self.session.query(CustomersModel.name, subquery.c.latest_order).join(subquery,
		                        CustomersModel.id == subquery.c.customer_id).all()
		self.assertEqual(query, [('Will Smith', '10-31-1998'), ('Tom Hanks', '10-15-1998')])
		ACL.unset_user()

	# SUBQUERY w JOIN, użytkownik powinien widzieć późniejsze zamówienia
	def test_same_lvl_subquery(self):
		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		customers = [
			CustomersModel(id=1, name='Will Smith', phone_number='111-222-333'),
			CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')
		]
		self.session.add_all(customers)
		self.session.commit()

		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998')
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='tradsjun2'))
		orders = [
			OrdersModel(id=5, customer_id=1, order_date='10-31-1998'),
			OrdersModel(id=6, customer_id=2, order_date='10-15-1998'),
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		subquery = self.session.query(OrdersModel.customer_id, func.max(OrdersModel.order_date).label('latest_order')
		                        ).group_by(OrdersModel.customer_id).subquery()
		query = self.session.query(CustomersModel.name, subquery.c.latest_order).join(subquery,
		                        CustomersModel.id == subquery.c.customer_id).all()
		self.assertEqual(query, [('Will Smith', '10-31-1998'), ('Tom Hanks', '10-15-1998')])
		ACL.unset_user()

	# HAVING, gdzie użytkownikowi się nie udaje, bo nie ma dostępu do tego klienta
	# (pytamy o id klientów, którzy mają więcej niż 2 zamówienia)
	def test_high_lvl_having(self):
		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998')
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='trads'))
		orders = [
			OrdersModel(id=5, customer_id=2, order_date='09-15-1998'),
			OrdersModel(id=6, customer_id=2, order_date='10-15-1998'),
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		query = self.session.query(OrdersModel.customer_id, func.count(OrdersModel.customer_id)).\
		                group_by(OrdersModel.customer_id).having(func.count(OrdersModel.customer_id) > 2).all()
		self.assertEqual(query, [])
		ACL.unset_user()

	# HAVING, gdzie użytkownikowi się udaje, bo ma wyższy poziom dostępu
	# (pytamy o id klientów, którzy mają więcej niż 2 zamówienia)
	def test_low_lvl_having(self):
		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998')
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='trads'))
		orders = [
			OrdersModel(id=5, customer_id=2, order_date='09-15-1998'),
			OrdersModel(id=6, customer_id=2, order_date='10-15-1998'),
		]
		self.session.add_all(orders)
		self.session.commit()
		query = self.session.query(OrdersModel.customer_id, func.count(OrdersModel.customer_id)).\
		                group_by(OrdersModel.customer_id).having(func.count(OrdersModel.customer_id) > 2).all()
		self.assertEqual(query, [(2, 4)])
		ACL.unset_user()

	# HAVING, gdzie użytkownikowi się udaje, bo ma ten sam poziom dostępu
	# (pytamy o id klientów, którzy mają więcej niż 2 zamówienia)
	def test_same_lvl_having(self):
		ACL.set_user(ACL.Users.get(username='tradsjun1'))
		orders = [
			OrdersModel(id=1, customer_id=1, order_date='07-31-1998'),
			OrdersModel(id=2, customer_id=1, order_date='08-31-1998'),
			OrdersModel(id=3, customer_id=2, order_date='07-15-1998'),
			OrdersModel(id=4, customer_id=2, order_date='08-15-1998')
		]
		self.session.add_all(orders)
		self.session.commit()
		ACL.unset_user()

		ACL.set_user(ACL.Users.get(username='tradsjun2'))
		orders = [
			OrdersModel(id=5, customer_id=2, order_date='09-15-1998'),
			OrdersModel(id=6, customer_id=2, order_date='10-15-1998'),
		]
		self.session.add_all(orders)
		self.session.commit()
		query = self.session.query(OrdersModel.customer_id, func.count(OrdersModel.customer_id)).\
		                group_by(OrdersModel.customer_id).having(func.count(OrdersModel.customer_id) > 2).all()
		self.assertEqual(query, [(2, 4)])
		ACL.unset_user()


### DOCKER AND POSTGRES IMAGE REQUIRED ###
# for more see notes above setup.PostgresSetupMixin class
# if you want to skip this test case, simply comment it out (yes, there is probably better way of doing this ;) )
"""
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
"""


if __name__ == '__main__':
	unittest.main()
