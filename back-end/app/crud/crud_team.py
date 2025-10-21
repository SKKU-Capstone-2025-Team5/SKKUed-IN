from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import secrets # For generating tokens

from app.models.team import Team, TeamMember, TeamMemberRole, TeamMemberStatus, OpenPosition, Invitation, InvitationStatus
from app.models.notification import NotificationType
from app.schemas.team import TeamCreate, TeamUpdate, OpenPositionCreate, TeamMemberCreate, InvitationCreate
from app.schemas.notification import NotificationCreate
from app.crud.crud_notification import create_notification 
from app.crud.crud_user import get_user_by_email 

def get_team(db: Session, team_id: int) -> Optional[Team]:
    return db.query(Team).filter(Team.id == team_id).first()

def get_teams_by_user(db: Session, user_id: int) -> List[Team]:
    return db.query(Team).join(TeamMember).filter(TeamMember.user_id == user_id).all()

def get_public_teams(db: Session, skip: int = 0, limit: int = 100) -> List[Team]:
    return db.query(Team).filter(Team.is_public == True).offset(skip).limit(limit).all()

def create_team(db: Session, team_in: TeamCreate, leader_id: int) -> Team:
    # 팀 만들기 
    db_team = Team(
        name=team_in.name,
        description=team_in.description,
        is_public=team_in.is_public,
        member_limit=team_in.member_limit,
        leader_id=leader_id
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)

    # 팀 리더 - accepted 멤버로 추가
    leader_member = TeamMember(
        team_id=db_team.id,
        user_id=leader_id,
        role=TeamMemberRole.LEADER,
        status=TeamMemberStatus.ACCEPTED
    )
    db.add(leader_member)
    db.commit()
    db.refresh(leader_member)

    # 뉴 멤버 refresh
    db.refresh(db_team)

    # 리더한테 팀 생성 알림 
    notification_in = NotificationCreate(
        user_id=leader_id,
        type=NotificationType.TEAM_STATUS_CHANGED,
        entity_type="Team",
        entity_id=db_team.id,
        message=f"Your team '{db_team.name}' has been created.",
        deep_link=f"/teams/{db_team.id}"
    )
    create_notification(db, notification_in=notification_in)

    return db_team

def update_team(db: Session, team: Team, team_in: TeamUpdate) -> Team:
    # 팀 정보 업데이트
    update_data = team_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(team, field, value)
    
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

def delete_team(db: Session, team_id: int) -> None:
    # 팀 삭제 
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if db_team:
        db.delete(db_team)
        db.commit()

def get_team_member(db: Session, team_id: int, user_id: int) -> Optional[TeamMember]:
    # 특정 멤버 가져오기 
    return db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id).first()

def create_team_member(db: Session, team_member_in: TeamMemberCreate, status: TeamMemberStatus) -> TeamMember:
    """
    Create a new team member with a specific status.
    If status is PENDING_APPLICATION, notify the team leader.
    """
    db_team_member = TeamMember(
        team_id=team_member_in.team_id,
        user_id=team_member_in.user_id,
        role=team_member_in.role,
        status=status
    )
    db.add(db_team_member)
    db.commit()
    db.refresh(db_team_member)

    if status == TeamMemberStatus.PENDING_APPLICATION:
        team = get_team(db, team_member_in.team_id)
        if team:
            notification_in = NotificationCreate(
                user_id=team.leader_id,
                type=NotificationType.APPLICATION_CREATED,
                entity_type="TeamMember",
                entity_id=db_team_member.id,
                message=f"New application to your team '{team.name}' from user {team_member_in.user_id}.",
                deep_link=f"/teams/{team.id}/applications"
            )
            create_notification(db, notification_in=notification_in)

    return db_team_member

def update_team_member_status(db: Session, team_member: TeamMember, new_status: TeamMemberStatus) -> TeamMember:
    # 팀 멤버 업데이트 & 알림 
    old_status = team_member.status
    team_member.status = new_status
    db.add(team_member)
    db.commit()
    db.refresh(team_member)

    if old_status != new_status:
        team = get_team(db, team_member.team_id)
        if team:
            if new_status == TeamMemberStatus.ACCEPTED:
                notification_type = NotificationType.APPLICATION_ACCEPTED
                message = f"Your application to team '{team.name}' has been accepted."
            elif new_status == TeamMemberStatus.REJECTED:
                notification_type = NotificationType.APPLICATION_REJECTED
                message = f"Your application to team '{team.name}' has been rejected."
            else:
                notification_type = None
                message = None
            
            if notification_type and message:
                notification_in = NotificationCreate(
                    user_id=team_member.user_id,
                    type=notification_type,
                    entity_type="TeamMember",
                    entity_id=team_member.id,
                    message=message,
                    deep_link=f"/teams/{team.id}"
                )
                create_notification(db, notification_in=notification_in)

    return team_member

def get_open_position(db: Session, position_id: int) -> Optional[OpenPosition]:
    # 특정 오픈 포지션 가져오기
    return db.query(OpenPosition).filter(OpenPosition.id == position_id).first()

def create_open_position(db: Session, open_position_in: OpenPositionCreate) -> OpenPosition:
    # 오픈 포지션 생성
    db_open_position = OpenPosition(
        team_id=open_position_in.team_id,
        role_name=open_position_in.role_name,
        required_skills=open_position_in.required_skills,
        required_count=open_position_in.required_count
    )
    db.add(db_open_position)
    db.commit()
    db.refresh(db_open_position)
    return db_open_position

def increment_filled_count(db: Session, open_position: OpenPosition) -> OpenPosition:
    # filled_count 증가
    open_position.filled_count += 1
    db.add(open_position)
    db.commit()
    db.refresh(open_position)
    return open_position

def decrement_filled_count(db: Session, open_position: OpenPosition) -> OpenPosition:
    # filled_count 감소
    if open_position.filled_count > 0:
        open_position.filled_count -= 1
        db.add(open_position)
        db.commit()
        db.refresh(open_position)
    return open_position

def create_invitation(db: Session, team_id: int, email: str, expires_delta: int = 72) -> Invitation:
    # 초대장 생성
    token = secrets.token_urlsafe(32) # secure URL-safe token 생성 
    expires_at = datetime.utcnow() + timedelta(hours=expires_delta)
    db_invitation = Invitation(
        team_id=team_id,
        email=email,
        token=token,
        expires_at=expires_at,
        status=InvitationStatus.PENDING
    )
    db.add(db_invitation)
    db.commit()
    db.refresh(db_invitation)

    # 팀 리더한테 알림 
    team = get_team(db, team_id)
    if team:
        notification_in_leader = NotificationCreate(
            user_id=team.leader_id,
            type=NotificationType.INVITATION_SENT,
            entity_type="Invitation",
            entity_id=db_invitation.id,
            message=f"An invitation to team '{team.name}' has been sent to {email}.",
            deep_link=f"/teams/{team.id}/invitations"
        )
        create_notification(db, notification_in=notification_in_leader)

        # 팀 멤버한테 알림 
        invited_user = get_user_by_email(db, email=email)
        if invited_user:
            notification_in_invited = NotificationCreate(
                user_id=invited_user.id,
                type=NotificationType.INVITATION_SENT,
                entity_type="Invitation",
                entity_id=db_invitation.id,
                message=f"You have been invited to join team '{team.name}'.",
                deep_link=f"/invitations/{token}"
            )
            create_notification(db, notification_in=notification_in_invited)

    return db_invitation

def get_invitation_by_token(db: Session, token: str) -> Optional[Invitation]:
    """Get an invitation by its unique token."""
    return db.query(Invitation).filter(Invitation.token == token).first()

def update_invitation_status(db: Session, invitation: Invitation, new_status: InvitationStatus) -> Invitation:
    """Update the status of an invitation and send notifications."""
    old_status = invitation.status
    invitation.status = new_status
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    if old_status != new_status:
        team = get_team(db, invitation.team_id)
        if team:
            # 리더한테 알림 
            if new_status == InvitationStatus.ACCEPTED:
                notification_type_leader = NotificationType.INVITATION_ACCEPTED
                message_to_leader = f"Invitation to team '{team.name}' for {invitation.email} has been accepted."
            elif new_status == InvitationStatus.REJECTED:
                notification_type_leader = NotificationType.INVITATION_REJECTED
                message_to_leader = f"Invitation to team '{team.name}' for {invitation.email} has been rejected."
            else:
                notification_type_leader = None
                message_to_leader = None
            
            if notification_type_leader and message_to_leader:
                notification_in_leader = NotificationCreate(
                    user_id=team.leader_id,
                    type=notification_type_leader,
                    entity_type="Invitation",
                    entity_id=invitation.id,
                    message=message_to_leader,
                    deep_link=f"/teams/{team.id}/invitations"
                )
                create_notification(db, notification_in=notification_in_leader)

            # 멤버한테 알림 
            invited_user = get_user_by_email(db, email=invitation.email)
            if invited_user:
                if new_status == InvitationStatus.ACCEPTED:
                    notification_type_invited = NotificationType.INVITATION_ACCEPTED
                    message_to_invited = f"You have accepted the invitation to team '{team.name}'."
                elif new_status == InvitationStatus.REJECTED:
                    notification_type_invited = NotificationType.INVITATION_REJECTED
                    message_to_invited = f"You have rejected the invitation to team '{team.name}'."
                else:
                    notification_type_invited = None
                    message_to_invited = None

                if notification_type_invited and message_to_invited:
                    notification_in_invited = NotificationCreate(
                        user_id=invited_user.id,
                        type=notification_type_invited,
                        entity_type="Invitation",
                        entity_id=invitation.id,
                        message=message_to_invited,
                        deep_link=f"/teams/{team.id}"
                    )
                    create_notification(db, notification_in=notification_in_invited)

    return invitation