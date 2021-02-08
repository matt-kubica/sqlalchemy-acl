# plik pomocniczy do testowania tworzenia bazy i zapytań w sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CustomersModel, OrdersModel
from sqlalchemy import func

engine = create_engine('sqlite:///test.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

CustomersModel.metadata.create_all(engine)
OrdersModel.metadata.create_all(engine)

cl1 = CustomersModel(id=1, name='Will Smith', phone_number='111-222-333')
cl2 = CustomersModel(id=2, name='Tom Hanks', phone_number='999-888-777')

ord1 = OrdersModel(id=1, customer_id=1, order_date='07-31-1998')
ord2 = OrdersModel(id=2, customer_id=1, order_date='08-31-1998')
ord3 = OrdersModel(id=3, customer_id=2, order_date='07-15-1998')
ord4 = OrdersModel(id=4, customer_id=2, order_date='08-15-1998')
ord5 = OrdersModel(id=5, customer_id=2, order_date='08-28-1998')

session.add_all([cl1, cl2, ord1, ord2, ord3, ord4, ord5])
session.commit()

# --- JOIN ---
# result = session.query(CustomersModel.name,
#                        OrdersModel.id, OrdersModel.order_date).join(OrdersModel).all()
# print(result)
# print(result[0]._asdict())
# print(result[0] == ('Will Smith', 1, '07-31-1998'))

# --- UPDATE ---
# session.query(CustomersModel).filter(CustomersModel.id == 1).update({'name': 'Smill With'})
# session.commit()

# --- GROUPBY ---
# result = session.query(CustomersModel.id, func.count(CustomersModel.id)).join(OrdersModel,
#            CustomersModel.id==OrdersModel.customer_id).group_by(CustomersModel.id).all()
# print(result)

# --- PODZAPYTANIE W JOIN ---
# sqlite> SELECT c.name, l.latest_order FROM customers c JOIN (
#    ...> SELECT customer_id, MAX(order_date) AS latest_order FROM orders GROUP BY customer_id)
#   ...> AS l
#   ...> ON c.id = l.customer_id;
# name|latest_order
# Will Smith|2021-02-01
# Denzel Washington|2021-02-02
# Mel Gibson|2021-02-03
# subquery = session.query(OrdersModel.customer_id, func.max(OrdersModel.order_date).label('latest_order')
#                        ).group_by(OrdersModel.customer_id).subquery()
# query = session.query(CustomersModel.name, subquery.c.latest_order).join(subquery,
#                        CustomersModel.id == subquery.c.customer_id).all()
# print(query)

# --- HAVING ---
# sqlite> SELECT customer_id, COUNT(*)
#   ...> FROM orders
#   ...> GROUP BY customer_id
#   ...> HAVING COUNT(*) > 2;
# 1|3
query = session.query(OrdersModel.customer_id, func.count(OrdersModel.customer_id)).\
                group_by(OrdersModel.customer_id).having(func.count(OrdersModel.customer_id) > 2)

print(query)
print(query.all())
