# app/api/v1/endpoints/recommend.py
from typing import Any, List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.user import User
from app.recsys.matcher import UserMatcher, MatchConfig
from app.schemas.user import UserWithSimilarity  # 추가

router = APIRouter()


@router.get("/", response_model=List[UserWithSimilarity])
def recommend_users(
    topk: int = Query(5, ge=1, le=50, description="반환할 추천 유저 수"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    현재 로그인한 유저 기준으로 추천 유저 + similarity 점수 반환.
    """
    # 1) DB에서 전체 유저 로드
    users = crud.user.get_multi(db, limit=None)
    print(f"[DEBUG] Total users fetched: {len(users)}")
    print(f"[DEBUG] Current user ID: {current_user.id}")

    if not users:
        return []

    # 2) SQLAlchemy User -> DataFrame 변환
    user_data = [
        {
            "user_id": user.id,
            "name": user.full_name,
            "major": (user.major or ""),
            "skills": ";".join([skill.name for skill in user.skills]),
            "interests": ";".join([interest.name for interest in user.interests]),
        }
        for user in users
    ]
    users_df = pd.DataFrame(user_data)
    print(f"[DEBUG] Users DataFrame head:\n{users_df.head()}")

    # 3) 매처 구성
    cfg = MatchConfig.from_values(topk=topk)
    matcher = UserMatcher(users_df, cfg)

    try:
        # 4) 현재 유저 기준 top-k 추천 (여기에 similarity 포함됨)
        recommended_user_info = matcher.topk_for(current_user.id, topk=topk)
        print(f"[DEBUG] Recommended user info length: {len(recommended_user_info)}")

        # user_id -> similarity 매핑
        sim_map = {item["user_id"]: item["similarity"] for item in recommended_user_info}
        recommended_ids_in_order = [item["user_id"] for item in recommended_user_info]

        # 5) DB에서 실제 User 객체 로드
        #    (get_multi_by_ids가 정렬을 유지 안 할 수도 있으니 dict로 받자)
        recommended_users = crud.user.get_multi_by_ids(db, ids=recommended_ids_in_order)
        user_dict = {u.id: u for u in recommended_users}

        # 6) top-k 순서를 유지하면서 UserWithSimilarity 리스트 구성
        result: List[UserWithSimilarity] = []
        for uid in recommended_ids_in_order:
            u = user_dict.get(uid)
            if u is None:
                continue  # 혹시 DB에 없으면 스킵

            sim = sim_map.get(uid, 0.0)

            result.append(
                UserWithSimilarity(
                    id=u.id,
                    email=u.email,
                    full_name=u.full_name,
                    major=u.major,
                    age=u.age,
                    phone_number=u.phone_number,
                    introduction=u.introduction,
                    profile_image_url=u.profile_image_url,
                    phone_number_public=u.phone_number_public,
                    age_public=u.age_public,
                    skills=list(u.skills),         # Pydantic이 Skill 모델로 변환해줌
                    interests=list(u.interests),   # Pydantic이 Interest 모델로 변환해줌
                    similarity=sim,
                )
            )

        print(f"[DEBUG] Returning {len(result)} users with similarity")
        return result

    except ValueError as e:
        # current_user가 users_df에 없을 때 등
        raise HTTPException(status_code=404, detail=str(e))