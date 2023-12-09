from database import db, Base
from sqlalchemy import Column, Integer, Table, ForeignKey, Boolean
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
    is_intern = db.Column(Boolean)
    is_extern = db.Column(Boolean)
    has_resume = db.Column(Boolean)
    enabled = db.Column(Boolean, default=True)
    reset_code = db.Column(db.String(180))
    reset_code_expiration = db.Column(db.String(180))
    roles = relationship('Role', secondary=user_roles, back_populates='users')