from database import db
from sqlalchemy import ForeignKey, Date


class Experience(db.Model):
    __tablename__ = 'experience'
    id = db.Column(db.Integer, primary_key=True)
    jobTitle = db.Column(db.String(150))
    company = db.Column(db.String(150))
    starting_year = db.Column(Date)
    ongoing = db.Column(db.Integer)
    ending_year = db.Column(Date)
    role = db.Column(db.String(210))
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
