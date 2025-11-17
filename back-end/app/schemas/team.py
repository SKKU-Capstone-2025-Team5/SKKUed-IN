from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from app.models.team import TeamStatus, TeamMemberRole, TeamMemberStatus, InvitationStatus

from app.schemas.user import UserInDBBase # Import UserInDBBase
from app.schemas.contest import Contest # Import Contest schema

# Team Schemas
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True
    member_limit: int

class TeamCreate(TeamBase):
    contest_id: Optional[int] = None

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    member_limit: Optional[int] = None
    status: Optional[TeamStatus] = None
    leader_id: Optional[int] = None
    contest_id: Optional[int] = None

class TeamRead(TeamBase):
    id: int
    status: TeamStatus
    leader_id: int
    leader: UserInDBBase # Add this line
    created_at: datetime
    updated_at: Optional[datetime] = None
    contest_id: Optional[int] = None
    contest: Optional[Contest] = None

    members: List["TeamMemberRead"] = [] # Add this line

    class Config:
        from_attributes = True

# OpenPosition Schemas
class OpenPositionBase(BaseModel):
    role_name: str
    required_skills: Optional[str] = None
    required_count: int = 1

class OpenPositionCreate(OpenPositionBase):
    team_id: Optional[int] = None 

class OpenPositionRead(OpenPositionBase):
    id: int
    team_id: int
    filled_count: int 

    class Config:
        from_attributes = True

# TeamMember Schemas
class TeamMemberBase(BaseModel):
    user_id: int
    role: TeamMemberRole = TeamMemberRole.MEMBER

class TeamMemberCreate(TeamMemberBase):
    team_id: Optional[int] = None 

class TeamMemberRead(TeamMemberBase):
    id: int
    team_id: int
    status: TeamMemberStatus # New field
    user: UserInDBBase # Add this line

    class Config:
        from_attributes = True

# Invitation Schemas
class InvitationBase(BaseModel):
    email: str

class InvitationCreate(InvitationBase):
    team_id: Optional[int] = None 

    class Config:
        from_attributes = True

class InvitationRead(InvitationBase):
    id: int
    team_id: int
    status: InvitationStatus
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

class InvitationStatusRead(BaseModel):
    status: InvitationStatus

    class Config:
        from_attributes = True