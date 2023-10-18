from database import db, Base
from sqlalchemy import Column, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship


user_roles = Table('user_roles', Base.metadata,
                   Column('user_id', Integer, ForeignKey('user.id')),
                   Column('role_id', Integer, ForeignKey('role.id'))
                   )

user_skills = Table('user_skills', Base.metadata,
                    Column('user_id', Integer, ForeignKey('user.id')),
                    Column('skill_id', Integer, ForeignKey('skill.id'))
                    )


class User(Base):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(180), unique=True, nullable=False)
    password = db.Column(db.String(220), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

