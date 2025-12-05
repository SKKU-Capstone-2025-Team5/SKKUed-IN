from typing import List, Any
from datetime import datetime
import pandas as pd

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.user import User
from app.models.team import TeamMemberStatus, InvitationStatus
from app.recsys.matcher import UserMatcher, MatchConfig
from app.crud.crud_message import crud_message
from app.schemas.message import MessageCreate, ConversationCreate
from app.models.message import ConversationType

router = APIRouter()

@router.post("/", response_model=schemas.TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    *, # force keyword arguments
    db: Session = Depends(deps.get_db),
    team_in: schemas.TeamCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new team.
    The current user will be set as the team leader.
    """
    team = crud.team.create_team(db=db, team_in=team_in, leader_id=current_user.id)
    return team

@router.get("/my", response_model=List[schemas.TeamRead])
def read_my_teams(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all teams where the current user is a leader or a member.
    """
    teams = crud.team.get_teams_by_user(db, user_id=current_user.id)
    return teams

@router.get("/public", response_model=List[schemas.TeamRead])
def read_public_teams(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve public teams.
    """
    teams = crud.team.get_public_teams(db, skip=skip, limit=limit)
    return teams

@router.get("/by_contest/{contest_id}", response_model=List[schemas.TeamRead])
def read_teams_by_contest(
    contest_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve teams by contest ID.
    """
    teams = crud.team.get_teams_by_contest_id(db, contest_id=contest_id, skip=skip, limit=limit)
    return teams

@router.get("/{team_id}", response_model=schemas.TeamRead)
def read_team(
    team_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user), # To ensure user is logged in
) -> Any:
    """
    Get a specific team by ID.
    """
    team = crud.team.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    # TODO: Add logic to check if the user has permission to view the team if it's private
    return team

@router.put("/{team_id}", response_model=schemas.TeamRead)
def update_team(
    team_id: int,
    team_in: schemas.TeamUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a team. Only the team leader can update it.
    """
    team = crud.team.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.leader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    team = crud.team.update_team(db=db, team=team, team_in=team_in)
    return team

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> None:
    """
    Delete a team. Only the team leader can delete it.
    """
    team = crud.team.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.leader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    crud.team.delete_team(db=db, team_id=team_id)

@router.post("/{team_id}/apply", response_model=schemas.TeamMemberRead, status_code=status.HTTP_201_CREATED)
def apply_to_team(
    team_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Apply to a public team.
    """
    team = crud.team.get_team(db, team_id=team_id)
    if not team or not team.is_public:
        raise HTTPException(status_code=404, detail="Team not found or not public")
    if crud.team.get_team_member(db, team_id=team_id, user_id=current_user.id):
        raise HTTPException(status_code=400, detail="Already a member or application pending")
    
    team_member_in = schemas.TeamMemberCreate(user_id=current_user.id, team_id=team_id)
    team_member = crud.team.create_team_member(db, team_member_in=team_member_in, status=TeamMemberStatus.PENDING_APPLICATION)
    return team_member

@router.post("/{team_id}/invite", response_model=schemas.InvitationRead, status_code=status.HTTP_201_CREATED)
def invite_to_team(
    team_id: int,
    user_id_to_invite: int = Body(..., embed=True),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Invite a user to a team. Only the team leader can invite.
    """
    team = crud.team.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.leader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user_to_invite = db.query(User).filter(User.id == user_id_to_invite).first()
    if not user_to_invite:
        raise HTTPException(status_code=404, detail="User to invite not found")

    invitation = crud.team.create_invitation(db, team_id=team_id, email=user_to_invite.email)
    return invitation

@router.post("/invitations/{token}/respond", response_model=schemas.TeamMemberRead)
def respond_to_invitation(
    token: str,
    accept: bool,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Respond to a team invitation (accept or reject).
    """
    invitation = crud.team.get_invitation_by_token(db, token=token)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if invitation.expires_at < datetime.utcnow():
        crud.team.update_invitation_status(db, invitation, InvitationStatus.EXPIRED)
        raise HTTPException(status_code=400, detail="Invitation expired")
    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Invitation already responded to or invalid")

    team = crud.team.get_team(db, team_id=invitation.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Find or create a DM conversation between the leader and the current user
    participant_ids = sorted([team.leader_id, current_user.id])
    conversation = crud_message.get_conversation_by_participants(db, participant_ids)
    if not conversation:
        conversation_in = ConversationCreate(participant_ids=participant_ids, type=ConversationType.DM)
        conversation = crud_message.create_conversation(db, conversation_in=conversation_in, current_user_id=current_user.id)

    if accept:
        # Check if user is already a member
        if crud.team.get_team_member(db, team_id=invitation.team_id, user_id=current_user.id):
            raise HTTPException(status_code=400, detail="Already a member of this team")
        
        # Create team member
        team_member_in = schemas.TeamMemberCreate(user_id=current_user.id, team_id=invitation.team_id)
        team_member = crud.team.create_team_member(db, team_member_in=team_member_in, status=TeamMemberStatus.ACCEPTED)
        crud.team.update_invitation_status(db, invitation, InvitationStatus.ACCEPTED)

        # Send message to leader
        if conversation:
            message_content = f"Accepted invitation to join {team.name}!"
            message_in = MessageCreate(conversation_id=conversation.id, content=message_content)
            crud_message.create_message(db, message_in=message_in, sender_id=current_user.id)

        return team_member
    else:
        crud.team.update_invitation_status(db, invitation, InvitationStatus.REJECTED)

        raise HTTPException(status_code=200, detail="Invitation rejected") # Return 200 for rejection

@router.get("/invitations/{token}/status", response_model=schemas.InvitationStatusRead)
def get_invitation_status(
    token: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get the status of an invitation.
    """
    invitation = crud.team.get_invitation_by_token(db, token=token)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    return invitation

@router.post("/{team_id}/applications/{team_member_id}/respond", response_model=schemas.TeamMemberRead)
def respond_to_application(
    team_id: int,
    team_member_id: int,
    accept: bool,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Leader responds to a team application (accept or reject).
    """
    team = crud.team.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.leader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    team_member = db.query(crud.team.TeamMember).filter(crud.team.TeamMember.id == team_member_id, crud.team.TeamMember.team_id == team_id).first()
    if not team_member:
        raise HTTPException(status_code=404, detail="Application not found")
    if team_member.status != TeamMemberStatus.PENDING_APPLICATION:
        raise HTTPException(status_code=400, detail="Application already responded to or invalid")
    
    if accept:
        # Check if team is full
        if len(team.members) >= team.member_limit:
            raise HTTPException(status_code=400, detail="Team is full")
        
        updated_team_member = crud.team.update_team_member_status(db, team_member, TeamMemberStatus.ACCEPTED)
        return updated_team_member
    else:
        updated_team_member = crud.team.update_team_member_status(db, team_member, TeamMemberStatus.REJECTED)
        return updated_team_member

@router.post("/{team_id}/open_positions/", response_model=schemas.OpenPositionRead, status_code=status.HTTP_201_CREATED)
def create_open_position(
    team_id: int,
    open_position_in: schemas.OpenPositionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new open position for a team. Only the team leader can create open positions.
    """
    team = crud.team.get_team(db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.leader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    open_position_in.team_id = team_id # Ensure team_id is set from path
    open_position = crud.team.create_open_position(db, open_position_in=open_position_in)
    return open_position