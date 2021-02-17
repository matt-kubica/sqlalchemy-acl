# plik generujący przykładową bazę danych, na której używana będzie nasza biblioteka

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import *
from sqlalchemy import func

engine = create_engine('sqlite:///external.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# klienci
print(session.query(CustomersModel.id, CustomersModel.name, CustomersModel.phone_number).all())

# zarobki
result = session.query(SalariesModel.id, SalariesModel.name, SalariesModel.salary).all()
for row in result:
    print(row[2])

# pudełka z zawartością
print(session.query(BoxesModel.name, ContentModel.chocolate_name).join(ContentModel,
                            BoxesModel.id == ContentModel.box_id).all())

# średnia liczba zamówionych sztuk artykułu na klienta
# sqlite> SELECT c.name, AVG(a.quantity) FROM customers c
# JOIN orders o ON c.id = o.customer_id
# JOIN articles a ON o.id = a.order_id
# GROUP BY c.id;
# Will Smith|11.25
# Denzel Washington|15.0
# Mel Gibson|10.0
result = session.query(CustomersModel.name, func.avg(ArticlesModel.quantity)).\
            join(OrdersModel, CustomersModel.id == OrdersModel.customer_id).\
            join(ArticlesModel, OrdersModel.id == ArticlesModel.order_id).\
            group_by(CustomersModel.id).all()
print(result)

# najpóźniejsze zamówienie klienta
# sqlite> SELECT c.name, MAX(o.order_date) FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id;
# Will Smith|2021-03-01
# Denzel Washington|2021-02-02
# Mel Gibson|2021-02-03
result = session.query(CustomersModel.name, func.max(OrdersModel.order_date)).\
            join(OrdersModel, CustomersModel.id == OrdersModel.customer_id).\
            group_by(CustomersModel.id).all()
print(result)
