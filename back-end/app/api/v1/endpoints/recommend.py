#from typing import Any, List
from typing import Any, List, Optional
import pandas as pd
#from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

#from app import crud, schemas
from app import crud
from app.api import deps
#from app.models.user import User
from app.models.user import User as UserModel
from app.schemas.user import RecommendedUser, User as UserSchema
from app.schemas.skill import Skill as SkillSchema
from app.schemas.interest import Interest as InterestSchema
from app.recsys.matcher import UserMatcher, MatchConfig

router = APIRouter()


#@router.get("/", response_model=List[schemas.User])
#@router.get("/", response_model=List[schemas.RecommendedUser])
@router.get("/", response_model=List[RecommendedUser])
def recommend_users(
    db: Session = Depends(deps.get_db),
    #current_user: User = Depends(deps.get_current_user),
    current_user: UserModel = Depends(deps.get_current_user),
    user_id: Optional[int] = Query(None, description="디버그용: 특정 user_id로 강제 추천"), #str -> int, DB에서는 INT임
    topk: int = Query(5, ge=1, le=50, description="반환할 추천 수"),
    w_major: Optional[float] = Query(None),
    w_skills: Optional[float] = Query(None),
    w_interests: Optional[float] = Query(None),
) -> Any:
    """
    Recommend users to the current user.
    """
    # 1) 추천 기준 user_id 결정
    base_user_id = user_id or current_user.id
    print(f"[DEBUG] base_user_id={base_user_id}, topk={topk}")


    # 2) 모든 사용자 로드
    users = crud.user.get_multi(db, limit=None)
    print(f"[DEBUG] Total users fetched: {len(users)}")
    print(f"[DEBUG] Current user ID: {current_user.id}")

    if not users:
        return []
    # 3) DataFrame으로 변환
    # Convert user data to pandas DataFrame

    '''
    user_data = [
        {
            "user_id": user.id,
            "name": user.full_name,
            "major": user.major,
            "skills": ";".join([skill.name for skill in user.skills]),
            "interests": ";".join([interest.name for interest in user.interests]),
        }
        for user in users
    ]
    users_df = pd.DataFrame(user_data)
    print(f"[DEBUG] Users DataFrame head:\n{users_df.head()}")

    # Configure and run the matcher
    cfg = MatchConfig(topk=5) # Get top 5 recommendations
    matcher = UserMatcher(users_df, cfg)

    try:
        recommended_user_info = matcher.topk_for(current_user.id)
        print(f"[DEBUG] Recommended user info length: {len(recommended_user_info)}")
        recommended_user_ids = [user['user_id'] for user in recommended_user_info]
        
        # Fetch full user objects from the database
        recommended_users = crud.user.get_multi_by_ids(db, ids=recommended_user_ids)
        print(f"[DEBUG] Recommended users being returned: {recommended_users}")
        return recommended_users
    except ValueError as e:
        # This can happen if the current user is not in the user list for some reason
        raise HTTPException(status_code=404, detail=str(e))
    '''
    user_rows = []
    for u in users:
        user_rows.append({
            "user_id": u.id,
            "name": u.full_name,
            "major": u.major or "",
            "skills": ";".join([s.name for s in u.skills]),
            "interests": ";".join([i.name for i in u.interests]),
        })
    users_df = pd.DataFrame(user_rows)
    print(f"[DEBUG] Users DF head:\n{users_df.head()}")

    # 기준 user가 DF에 없으면 에러
    if base_user_id not in set(users_df["user_id"]):
        raise HTTPException(status_code=404, detail=f"user_id '{base_user_id}' not found")

    # 4) 매처 실행
    #cfg = MatchConfig(topk=topk)
    cfg = MatchConfig.from_values(
        w_major=w_major,
        w_skills=w_skills,
        w_interests=w_interests,
        topk=topk
    )
    matcher = UserMatcher(users_df, cfg)

    try:
        rec_info = matcher.topk_for(base_user_id, topk=topk)
        rec_ids = [r["user_id"] for r in rec_info]
        print(f"[DEBUG] rec_ids={rec_ids}")

        # 5) DB에서 최종 객체 조회 → 스키마로 반환
        #rec_models = crud.user.get_multi_by_ids(db, ids=rec_ids)
        # 보통 orm_mode 켜져 있으면 아래 변환 없이도 OK. 혹시 불안하면 다음 줄 사용:
        # return [schemas.User.model_validate(m) for m in rec_models]
        #-------------
        
        # Similarity 매핑
        id_to_sim = {r["user_id"]: float(r["similarity"]) for r in rec_info}

        # DB 모델 조회
        rec_models = crud.user.get_multi_by_ids(db, ids=rec_ids)

        # 추천 순서 유지
        id_pos = {uid: i for i, uid in enumerate(rec_ids)}
        rec_models.sort(key=lambda m: id_pos.get(m.id, 1e9))

        # RecommendedUser 스키마로 변환해 반환
        '''
        out = []
        for m in rec_models:
            out.append(
                #schemas.RecommendedUser(
                RecommendedUser(
                    id=m.id,
                    email=m.email,
                    full_name=m.full_name,
                    major=m.major,
                    profile_image_url=m.profile_image_url,
                    skills=[schemas.skill.Skill(id=s.id, name=s.name) for s in m.skills],
                    interests=[schemas.interest.Interest(id=i.id, name=i.name) for i in m.interests],
                    similarity=id_to_sim[m.id],     
                )
            )
        return out
        '''
        sim_map = {r["user_id"]: float(r["similarity"]) for r in rec_info}

        resp: List[RecommendedUser] = []
        for m in rec_models:
            resp.append(
                RecommendedUser(
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
                    similarity=round(sim_map.get(m.id, 0.0), 4),
                )
            )

        return resp
        #--------------
        #return rec_models
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))