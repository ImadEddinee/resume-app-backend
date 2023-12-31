from database import db
from sqlalchemy import ForeignKey, Date, LargeBinary


class BasicInfo(db.Model):
    __tablename__ = 'basic_info'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    age = db.Column(db.Integer)
    social_status = db.Column(db.String(150))
    occupation = db.Column(db.String(150))
    years_of_exp = db.Column(db.Integer)
    birth_date = db.Column(db.String(150))
    resume_picture = db.Column(db.String(255))
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
