
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint

from .base import DeclarativeBase


# association for many-to-many relationship
association_table = Table('association', DeclarativeBase.metadata,
                          Column('access_level_id', Integer, ForeignKey('access_level.id')),
                          Column('acl_entry_id', Integer, ForeignKey('acl_entry.id'))
                          )


class UserModelMixin(DeclarativeBase):
    __tablename__ = 'acl_user'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    access_level_id = Column(Integer, ForeignKey('access_level.id'))
    access_level = relationship('AccessLevelModel', back_populates='users')

    def __repr__(self):
        return '<User {0}:{1}>'.format(self.id, self.username)


class ACLEntryModel(DeclarativeBase):
    __tablename__ = 'acl_entry'

    id = Column(Integer, primary_key=True)
    dest_table = Column(String(64), nullable=False)
    dest_id = Column(Integer, nullable=False)

    access_levels = relationship('AccessLevelModel', secondary=association_table, back_populates='entries')
    __table_args__ = (UniqueConstraint('dest_table', 'dest_id'),)

    def __repr__(self):
        return '<ACLEntry {0} -> {1}:{2}>'.format(
            self.id,
            self.dest_table,
            self.dest_id
        )


class AccessLevelModel(DeclarativeBase):
    __tablename__ = 'access_level'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('access_level.id'))
    role_description = Column(String(64), nullable=True)

    children = relationship('AccessLevelModel', backref=backref('parent', remote_side=[id]))
    users = relationship('UserModelMixin', back_populates='access_level')
    entries = relationship('ACLEntryModel', secondary=association_table,
                           back_populates='access_levels')


    def __repr__(self):
        return '<AccessLevel {0}:{1}>'.format(
            self.id,
            self.role_description
        )