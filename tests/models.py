from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ExemplaryModel(Base):
	__tablename__ = 'testable-models'

	id = Column(Integer, primary_key=True)
	string_field = Column(String(64), unique=False, nullable=False)
	integer_field = Column(Integer, unique=False, nullable=False)

	def __repr__(self):
		return '<TestableModel {0}>'.format(self.id)