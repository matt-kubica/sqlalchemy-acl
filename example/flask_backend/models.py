import sys
sys.path.insert(0, '../..')

from sqlalchemy_acl.models import UserModelMixin
from . import db


class UpdateMixin():

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class UserModel(UserModelMixin, UpdateMixin):
    email = db.Column(db.String(64), unique=False, nullable=False)
    password_hash = db.Column(db.String(128), unique=False, nullable=False)

    def __init__(self, email, password_hash, **kwargs):
        self.email = email
        self.password_hash = password_hash
        super().__init__(**kwargs)



class SalaryModel(db.Model, UpdateMixin):
    __tablename__ = 'salaries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    salary = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, id, name, salary):
        self.id = id
        self.name = name
        self.salary = salary

    def __repr__(self):
        return f'<Salary({self.id}, {self.name}, {self.salary})>'


class CustomerModel(db.Model, UpdateMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False, nullable=False)
    phone_number = db.Column(db.String(20), unique=False, nullable=False)
    # children = relationship('OrdersModel', back_populates = 'parent')

    def __init__(self, id, name, phone_number):
        self.id = id
        self.name = name
        self.phone_number = phone_number

    def __repr__(self):
        return f'<Customer({self.id}, {self.name}, {self.phone_number})>'


class OrderModel(db.Model, UpdateMixin):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    order_date = db.Column(db.String(20), unique=False, nullable=False)
    # parent = relationship('ClientsModel', back_populates = 'children')

    def __init__(self, id, customer_id, order_date):
        self.id = id
        self.customer_id = customer_id
        self.order_date = order_date

    def __repr__(self):
        return f'<Order({self.id}, {self.customer_id}, {self.order_date})>'


class ArticleModel(db.Model, UpdateMixin):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    box_id = db.Column(db.Integer, db.ForeignKey('boxes.id'))
    quantity = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, id, order_id, box_id, quantity):
        self.id = id
        self.order_id = order_id
        self.box_id = box_id
        self.quantity = quantity

    def __repr__(self):
        return f'<Article({self.order_id}, {self.box_id}, {self.quantity})>'


class BoxModel(db.Model, UpdateMixin):
    __tablename__ = 'boxes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False, nullable=False)
    price = db.Column(db.Integer, unique=False, nullable=False)
    stock = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def __repr__(self):
        return f'<Box({self.id}, {self.name}, {self.price}, {self.stock})>'


class ContentModel(db.Model, UpdateMixin):
    __tablename__ = 'contents'

    id = db.Column(db.String(4), primary_key=True)
    box_id = db.Column(db.Integer, db.ForeignKey('boxes.id'))
    chocolate_name = db.Column(db.String(32), unique=True, nullable=False)
    quantity = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, id, box_id, chocolate_name, quantity):
        self.id = id
        self.box_id = box_id
        self.chocolate_name = chocolate_name
        self.quantity = quantity

    def __repr__(self):
        return f'<Content({self.box_id}, {self.chocolate_name}, {self.quantity})>'



