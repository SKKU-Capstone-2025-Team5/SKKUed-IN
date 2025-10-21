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


class TeamStatus(enum.Enum):
    RECRUITING = "recruiting"
    ACTIVE = "active"
    ARCHIVED = "archived"


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    # project_id will be added later when a Project model exists
    # project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    is_public = Column(Boolean, default=True)
    member_limit = Column(Integer, nullable=False)
    status = Column(Enum(TeamStatus), default=TeamStatus.RECRUITING, nullable=False)
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    leader = relationship("User", back_populates="led_teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    open_positions = relationship("OpenPosition", back_populates="team", cascade="all, delete-orphan")


class TeamMemberRole(enum.Enum):
    LEADER = "leader"
    MEMBER = "member"

class TeamMemberStatus(enum.Enum):
    PENDING_APPLICATION = "pending_application"
    PENDING_INVITATION = "pending_invitation"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(TeamMemberRole), default=TeamMemberRole.MEMBER, nullable=False)
    status = Column(Enum(TeamMemberStatus), default=TeamMemberStatus.ACCEPTED, nullable=False) # New status column
    
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="teams")


class OpenPosition(Base):
    __tablename__ = "open_positions"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    role_name = Column(String(100), nullable=False)
    required_skills = Column(Text) # Simple text field for now
    required_count = Column(Integer, default=1, nullable=False)
    filled_count = Column(Integer, default=0, nullable=False) # New filled_count column
    
    team = relationship("Team", back_populates="open_positions")


class InvitationStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    email = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    team = relationship("Team") # No back_populates needed for now