from sqlalchemy.orm import relationship

from database import db
from src.models.user_model import Base, user_roles


class Role(Base):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    users = relationship('User', secondary=user_roles, back_populates='roles')

    def to_dict(self):
        return {'id': self.id, 'name': self.name}