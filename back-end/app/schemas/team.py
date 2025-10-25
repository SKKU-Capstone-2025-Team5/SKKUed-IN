from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from app.models.team import TeamStatus, TeamMemberRole, TeamMemberStatus, InvitationStatus

# Team Schemas
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True
    member_limit: int

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    member_limit: Optional[int] = None
    status: Optional[TeamStatus] = None
    leader_id: Optional[int] = None

class TeamRead(TeamBase):
    id: int
    status: TeamStatus
    leader_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# OpenPosition Schemas
class OpenPositionBase(BaseModel):
    role_name: str
    required_skills: Optional[str] = None
    required_count: int = 1

class OpenPositionCreate(OpenPositionBase):
    team_id: Optional[int] = None # Will be set by the backend

class OpenPositionRead(OpenPositionBase):
    id: int
    team_id: int
    filled_count: int # New field

    class Config:
        from_attributes = True

# TeamMember Schemas
class TeamMemberBase(BaseModel):
    user_id: int
    role: TeamMemberRole = TeamMemberRole.MEMBER

class TeamMemberCreate(TeamMemberBase):
    team_id: Optional[int] = None # Will be set by the backend

class TeamMemberRead(TeamMemberBase):
    id: int
    team_id: int
    status: TeamMemberStatus # New field

    class Config:
        from_attributes = True

# Invitation Schemas
class InvitationBase(BaseModel):
    email: str

class InvitationCreate(InvitationBase):
    team_id: Optional[int] = None # Will be set by the backend

class InvitationRead(InvitationBase):
    id: int
    team_id: int
    token: str
    expires_at: datetime
    status: InvitationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True