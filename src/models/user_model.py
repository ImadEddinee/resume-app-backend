from datetime import datetime

from database import db, Base
from sqlalchemy import Column, Integer, Table, ForeignKey, Boolean, LargeBinary
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
    current_position = db.Column(db.String(120))
    is_intern = db.Column(Boolean)
    is_extern = db.Column(Boolean)
    has_resume = db.Column(Boolean)
    resume = db.Column(db.String(220))
    enabled = db.Column(Boolean, default=True)
    reset_code = db.Column(db.String(180))
    reset_code_expiration = db.Column(db.String(180))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    roles = relationship('Role', secondary=user_roles, back_populates='users')