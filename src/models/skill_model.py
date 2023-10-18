from database import db
from sqlalchemy.orm import relationship
from src.models.user_model import Base, user_skills


class Skill(Base):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), unique=True, nullable=False)
