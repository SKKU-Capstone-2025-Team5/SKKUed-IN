from typing import Any, List, Optional, Tuple
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models.user import User as UserModel
from app.models.team import Team, TeamMember, TeamMemberStatus, Invitation, InvitationStatus
from app.schemas.user import RecommendedUser
from app.schemas.skill import Skill as SkillSchema
from app.schemas.interest import Interest as InterestSchema
from app.recsys.matcher import UserMatcher, MatchConfig

router = APIRouter()

def _collect_interactions_for_user(db: Session, target_user_id: int) -> List[Tuple[int, int, int]]:
    """
    (target_user_id, other_user_id, label) 리스트 생성
    label: +1(ACCEPTED), -1(REJECTED)

    - target이 리더인 팀에서:
        * ACCEPTED 멤버 -> +1
        * REJECTED 멤버 -> -1
        * 초대(Invitation) ACCEPTED -> +1 / REJECTED -> -1
    - target이 어떤 팀의 멤버로 ACCEPTED 된 경우:
        * 같은 팀의 다른 ACCEPTED 멤버들과 상호 +1
    """
    interactions: List[Tuple[int, int, int]] = []

    # ---------- target이 리더인 팀 ----------
    leader_teams = db.query(Team).filter(Team.leader_id == target_user_id).all()
    team_ids = [t.id for t in leader_teams]

    # 팀 멤버 상태 기반
    if team_ids:
        tms = db.query(TeamMember).filter(TeamMember.team_id.in_(team_ids)).all()
        for tm in tms:
            if tm.user_id == target_user_id:
                continue
            if tm.status == TeamMemberStatus.ACCEPTED:
                interactions.append((target_user_id, tm.user_id, +1))
            elif tm.status == TeamMemberStatus.REJECTED:
                interactions.append((target_user_id, tm.user_id, -1))

        # 초대 기반 (이메일 -> 유저 id 매핑 필요)
        all_users = db.query(UserModel).all()
        email_to_uid = {u.email: u.id for u in all_users}
        invs = db.query(Invitation).filter(Invitation.team_id.in_(team_ids)).all()
        for inv in invs:
            uid = email_to_uid.get(inv.email)
            if uid is None or uid == target_user_id:
                continue
            if inv.status == InvitationStatus.ACCEPTED:
                interactions.append((target_user_id, uid, +1))
            elif inv.status == InvitationStatus.REJECTED:
                interactions.append((target_user_id, uid, -1))

    # ---------- target이 멤버로 참여한 팀(ACCEPTED) ----------
    my_memberships = (
        db.query(TeamMember)
        .filter(TeamMember.user_id == target_user_id,
                TeamMember.status == TeamMemberStatus.ACCEPTED)
        .all()
    )
    joined_team_ids = [tm.team_id for tm in my_memberships]
    if joined_team_ids:
        peers = (
            db.query(TeamMember)
            .filter(TeamMember.team_id.in_(joined_team_ids),
                    TeamMember.status == TeamMemberStatus.ACCEPTED)
            .all()
        )
        for peer in peers:
            if peer.user_id != target_user_id:
                interactions.append((target_user_id, peer.user_id, +1))

    # 중복 제거 (정확히 같은 3튜플 단위)
    interactions = list(dict.fromkeys(interactions))
    return interactions


@router.get("/", response_model=List[RecommendedUser])
def recommend_users(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user),
    user_id: Optional[int] = Query(None, description="디버그용: 특정 user_id로 강제 추천"),
    topk: int = Query(5, ge=1, le=50, description="반환할 추천 수"),
    w_major: Optional[float] = Query(None),
    w_skills: Optional[float] = Query(None),
    w_interests: Optional[float] = Query(None),
    learn: bool = Query(True, description="팀/초대 피드백으로 가중치 학습 여부"),
) -> Any:
    """
    사용자 추천 API
    - w_major/w_skills/w_interests 수동 지정 가능
    - learn=True면 팀/초대 기록으로 가중치 자동 학습 후 추천
    """
    base_user_id = user_id or current_user.id
    print(f"[DEBUG] base_user_id={base_user_id}, topk={topk}")

    users = crud.user.get_multi(db, limit=None)
    print(f"[DEBUG] Total users fetched: {len(users)} / current_user={current_user.id}")
    if not users:
        return []

    rows = [{
        "user_id": u.id,
        "name": u.full_name,
        "major": u.major or "",
        "skills": ";".join([s.name for s in u.skills]),
        "interests": ";".join([i.name for i in u.interests]),
    } for u in users]
    users_df = pd.DataFrame(rows)
    print(f"[DEBUG] Users DF head:\n{users_df.head()}")

    if base_user_id not in set(users_df["user_id"]):
        raise HTTPException(status_code=404, detail=f"user_id '{base_user_id}' not found")

    cfg = MatchConfig.from_values(
        w_major=w_major, w_skills=w_skills, w_interests=w_interests, topk=topk
    )
    matcher = UserMatcher(users_df, cfg)

    # 자동 학습 (← 매처의 learn_from_history 호출로 변경됨)
    if learn:
        interactions = _collect_interactions_for_user(db, base_user_id)
        print(f"[DEBUG] interactions for {base_user_id}: {len(interactions)}")
        if interactions:
            learned = matcher.learn_from_history(base_user_id, interactions)
            print(f"[DEBUG] learned weights -> {learned}")

    try:
        rec_info = matcher.topk_for(base_user_id, topk=topk)
        rec_ids = [r["user_id"] for r in rec_info]
        print(f"[DEBUG] rec_ids={rec_ids}")

        id_to_sim = {r["user_id"]: float(r["similarity"]) for r in rec_info}
        rec_models = crud.user.get_multi_by_ids(db, ids=rec_ids)

        # 추천 순서 유지
        id_pos = {uid: i for i, uid in enumerate(rec_ids)}
        rec_models.sort(key=lambda m: id_pos.get(m.id, 10**9))

        resp: List[RecommendedUser] = []
        for m in rec_models:
            resp.append(RecommendedUser(
                id=m.id,
                email=m.email,
                full_name=m.full_name,
                major=m.major,
                age=m.age,
                phone_number=m.phone_number,
                introduction=m.introduction,
                profile_image_url=m.profile_image_url,
                phone_number_public=m.phone_number_public,
                age_public=m.age_public,
                skills=[SkillSchema(id=s.id, name=s.name) for s in m.skills],
                interests=[InterestSchema(id=i.id, name=i.name) for i in m.interests],
                similarity=round(id_to_sim.get(m.id, 0.0), 4),
            ))
        return resp
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))