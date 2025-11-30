from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
#from app.db.base_class import Base


user_skill_association = Table(
    'user_skill', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('skill_id', Integer, ForeignKey('skill.id'))
)

user_interest_association = Table(
    'user_interest', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('interest_id', Integer, ForeignKey('interest.id'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    profile_image_url = Column(String, nullable=True)
    major = Column(String, nullable=True)
    age = Column(String, nullable=True) # Added missing column
    phone_number = Column(String, nullable=True) # Added missing column
    introduction = Column(String, nullable=True) # Added missing column
    phone_number_public = Column(Boolean(), default=True) # Added missing column
    age_public = Column(Boolean(), default=True) # Added missing column

    skills = relationship("Skill", secondary=user_skill_association, back_populates="users")
    interests = relationship("Interest", secondary=user_interest_association, back_populates="users")

    led_teams = relationship("Team", back_populates="leader")
    teams = relationship("TeamMember", back_populates="user")
    conversations = relationship(
        "Conversation",
        secondary="conversation_participant",
        back_populates="participants",
    )
    notifications = relationship("Notification", back_populates="recipient")
