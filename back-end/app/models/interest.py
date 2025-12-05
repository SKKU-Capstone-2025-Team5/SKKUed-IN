from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.user import user_interest_association # Import the association table

class Interest(Base):
    __tablename__ = "interest"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    users = relationship("User", secondary=user_interest_association, back_populates="interests")
