import datetime
import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db.base import Base

class ConversationType(str, enum.Enum):
    DM = "dm"
    TEAM = "team"

conversation_participant_association = Table(
    "conversation_participant",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("conversation_id", Integer, ForeignKey("conversations.id", ondelete="CASCADE"), primary_key=True),
)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ConversationType), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    participants = relationship(
        "User",
        secondary=conversation_participant_association,
        back_populates="conversations",
    )
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # Using JSON to store a list of user_ids who have read the message
    read_by = Column(JSON, default=[])

    sender = relationship("User")
    conversation = relationship("Conversation", back_populates="messages")
