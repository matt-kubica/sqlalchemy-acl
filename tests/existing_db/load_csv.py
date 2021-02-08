import sys
import os

sys.path.insert(0,'../..')
sys.path.insert(1,'..')

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_acl.models import ACLEntryModel
import csv

Base = declarative_base()

class ToyModel(Base):
    __tablename__ = 'toy'

    id = Column(Integer, primary_key=True)
    str = Column(String(16))

    def __repr__(self):
        return f'<ToyModel(id = {self.id}, str = {self.str})>'

class ACLEntryModel(Base):
    __tablename__ = 'acl_entry'

    id = Column(Integer, primary_key=True)
    dest_table = Column(String(64), nullable=False)
    dest_id = Column(Integer, nullable=False)

    def __repr__(self):
        return '<ACLEntry {0} -> {1}:{2}>'.format(
            self.id,
            self.dest_table,
            self.dest_id
        )

engine = create_engine('sqlite:///toy.db')
Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

with open('toy_db.csv', 'r', encoding="utf-8") as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')

    for row in csv_reader:
        record = ToyModel(id=int(row[0]),str=row[1])
        session.add(record)
        session.add(ACLEntryModel(dest_table = 'toy', dest_id = int(row[0]))) # create an ACLEntryModel record

        acl_ids = list(map(int, row[2].split(','))) # read future acl indices and convert str to int

        print('Do Association zostało by dodane:')
        for id in acl_ids:
            print(f'access_level_id = {id}, acl_entry_id = {int(row[0])}')


session.commit()
print(session.query(ACLEntryModel).all())
print(session.query(ToyModel).all())
os.remove('toy.db')
