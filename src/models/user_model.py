from database import db, Base
from sqlalchemy import Column, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship


user_roles = Table('user_roles', Base.metadata,
                   Column('user_id', Integer, ForeignKey('user.id')),
                   Column('role_id', Integer, ForeignKey('role.id'))
                   )


class User(Base):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(180), unique=True)
    password = db.Column(db.String(220))
    email = db.Column(db.String(120), unique=True)
    has_account = db.Column(db.Integer)
