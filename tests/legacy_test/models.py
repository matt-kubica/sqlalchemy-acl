# dodałem modele wszystkich tabel "zewnętrznych"

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ExemplaryModel(Base):
	__tablename__ = 'testable-models'

	id = Column(Integer, primary_key=True)
	string_field = Column(String(64), unique=False, nullable=False)
	integer_field = Column(Integer, unique=False, nullable=False)

	def __repr__(self):
		return '<TestableModel {0}>'.format(self.id)

class SalariesModel(Base):
	__tablename__ = 'salaries'

	id = Column(Integer, primary_key=True)
	name = Column(String(64), unique=True, nullable=False)
	salary = Column(Numeric(9,2), unique=False, nullable=False)

	def __repr__(self):
		return f'<Customer({self.id}, {self.name}, {self.salary})>'

class CustomersModel(Base):
	__tablename__ = 'customers'

	id = Column(Integer, primary_key=True)
	name = Column(String(64), unique=False, nullable=False)
	phone_number = Column(String(20), unique=False, nullable=False)

	# children = relationship('OrdersModel', back_populates = 'parent')

	def __repr__(self):
		return f'<Customer({self.id}, {self.name}, {self.phone_number})>'

class OrdersModel(Base):
	__tablename__ = 'orders'

	id = Column(Integer, primary_key=True)
	customer_id = Column(Integer, ForeignKey('customers.id'))
	order_date = Column(String(20), unique=False, nullable=False)

	# parent = relationship('ClientsModel', back_populates = 'children')

	def __repr__(self):
		return f'<Order({self.id}, {self.customer_id}, {self.order_date})>'

class ArticlesModel(Base):
	__tablename__ = 'articles'

	id = Column(Integer, primary_key=True)
	order_id = Column(Integer, ForeignKey('orders.id'))
	box_id = Column(Integer, ForeignKey('boxes.id'))
	quantity = Column(Integer, unique=False, nullable=False)

	def __repr__(self):
		return f'<Article({self.order_id}, {self.box_id}, {self.quantity})>'

class BoxesModel(Base):
	__tablename__ = 'boxes'

	id = Column(Integer, primary_key=True)
	name = Column(String(64), unique=False, nullable=False)
	price = Column(Numeric(7,2), unique=False, nullable=False)
	stock = Column(Integer, unique=False, nullable=False)

	def __repr__(self):
		return f'<Box({self.id}, {self.name}, {self.price}, {self.stock})>'

class ContentModel(Base):
	__tablename__ = 'content'

	id = Column(String(4), primary_key=True)
	box_id = Column(Integer, ForeignKey('boxes.id'))
	chocolate_name = Column(String(32), unique=True, nullable=False)
	quantity = Column(Integer, unique=False, nullable=False)

	def __repr__(self):
		return f'<Content({self.box_id}, {self.chocolate_name}, {self.quantity})>'
