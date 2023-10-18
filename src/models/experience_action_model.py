from database import db
from sqlalchemy import ForeignKey


class ExperienceAction(db.Model):
    __tablename__ = 'experience_action'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50))
    experience_id = db.Column(db.Integer, ForeignKey('experience.id'), nullable=False)
