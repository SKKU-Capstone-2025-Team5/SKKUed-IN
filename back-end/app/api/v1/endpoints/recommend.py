from typing import Any, List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.user import User
from app.recsys.matcher import UserMatcher, MatchConfig

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def recommend_users(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Recommend users to the current user.
    """
    users = crud.user.get_multi(db)
    
    if not users:
        return []

    # Convert user data to pandas DataFrame
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

    # Configure and run the matcher
    cfg = MatchConfig(topk=5) # Get top 5 recommendations
    matcher = UserMatcher(users_df, cfg)

    try:
        recommended_user_info = matcher.topk_for(current_user.id)
        recommended_user_ids = [user['user_id'] for user in recommended_user_info]
        
        # Fetch full user objects from the database
        recommended_users = crud.user.get_multi_by_ids(db, ids=recommended_user_ids)
        return recommended_users
    except ValueError as e:
        # This can happen if the current user is not in the user list for some reason
        raise HTTPException(status_code=404, detail=str(e))
