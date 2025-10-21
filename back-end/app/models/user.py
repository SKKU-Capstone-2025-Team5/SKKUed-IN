from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.message import conversation_participant_association

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    major = Column(String, nullable=True)
    age = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    introduction = Column(String(1000), nullable=True)
    profile_image_url = Column(String, nullable=True)

    core_skill_tags = Column(JSON, nullable=True)
    interests = Column(JSON, nullable=True)
    phone_number_public = Column(Boolean, default=False)
    age_public = Column(Boolean, default=False)

    conversations = relationship(
        "Conversation",
        secondary=conversation_participant_association,
        back_populates="participants",
    )

    led_teams = relationship("Team", back_populates="leader")
    teams = relationship("TeamMember", back_populates="user")
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")
