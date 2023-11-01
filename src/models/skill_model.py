from database import db
from sqlalchemy import ForeignKey


class Skill(db.Model):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), unique=True, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
