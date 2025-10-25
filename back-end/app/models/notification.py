
import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Enum,
    DateTime,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class NotificationType(enum.Enum):
    APPLICATION_CREATED = "application_created"
    APPLICATION_ACCEPTED = "application_accepted"
    APPLICATION_REJECTED = "application_rejected"
    INVITATION_SENT = "invitation_sent"
    INVITATION_ACCEPTED = "invitation_accepted"
    INVITATION_REJECTED = "invitation_rejected"
    NEW_MESSAGE = "new_message"
    ROLE_CHANGED = "role_changed"
    TEAM_STATUS_CHANGED = "team_status_changed"
    # 다른 컬럼 필요하면 추가 


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    entity_type = Column(String, nullable=False) # 'Team', 'TeamMember', 'Invitation', 'Message'
    entity_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True) # retention policy
    deep_link = Column(String, nullable=True)

    recipient = relationship("User", back_populates="notifications")
