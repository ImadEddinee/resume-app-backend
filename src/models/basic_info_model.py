from database import db
from sqlalchemy import ForeignKey, Date


class BasicInfo(db.Model):
    __tablename__ = 'basic_info'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer)
    social_status = db.Column(db.String(150))
    occupation = db.Column(db.String(150))
    years_of_exp = db.Column(db.Integer)
    birthdate = db.Column(Date)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
