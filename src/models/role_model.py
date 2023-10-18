from database import db
from src.models.user_model import Base


class Role(Base):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(150), nullable=False)
