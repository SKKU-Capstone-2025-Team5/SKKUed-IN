from typing import List, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.user.User = Depends(deps.get_current_user),
) -> models.user.User:
    """
    Get current user.
    """
    return current_user

@router.get("/search", response_model=List[schemas.User])
def search_users(
    query: str = Query(..., min_length=1),
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Search for users by full name or email.
    """
    users = crud.user.search_users(db, query=query)
    return users
