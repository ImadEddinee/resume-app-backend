from database import db
from sqlalchemy import ForeignKey


class Contact(db.Model):
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    phone_number = db.Column(db.String(150))
    linkedin = db.Column(db.String(150))
    address = db.Column(db.String(150))
    github = db.Column(db.String(150))

    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
