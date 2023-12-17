from database import db
from sqlalchemy import ForeignKey, Enum


class Language(db.Model):
    __tablename__ = 'language'
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(150))
    speak = db.Column(db.String(150))
    read = db.Column(db.String(150))
    write = db.Column(db.String(150))
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
