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
result = session.query(CustomersModel.name,
                        OrdersModel.id, OrdersModel.order_date).join(OrdersModel).all()
print(result)
print(result[0]._asdict())
print(result[0] == ('Will Smith', 1, '07-31-1998'))

# --- UPDATE ---
# session.query(CustomersModel).filter(CustomersModel.id == 1).update({'name': 'Smill With'})
# session.commit()

# --- GROUPBY ---
# result = session.query(CustomersModel.id, func.count(CustomersModel.id)).join(OrdersModel,
#            CustomersModel.id==OrdersModel.customer_id).group_by(CustomersModel.id).all()
# print(result)
