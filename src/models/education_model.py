from database import db
from sqlalchemy import ForeignKey, Date


class Education(db.Model):
    __tablename__ = 'education'
    id = db.Column(db.Integer, primary_key=True)
    degree_title = db.Column(db.String(150))
    institution = db.Column(db.String(150))
    starting_year = db.Column(db.String(150))
    ongoing = db.Column(db.Integer)
    graduating_year = db.Column(db.String(150))
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
