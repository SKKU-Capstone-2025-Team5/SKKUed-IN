from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models.user import User
from app.api import deps

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user's profile.
    """
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update current user's profile.
    """
    user = crud.update_user(db, db_user=current_user, user_in=user_in)
    return user

@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific user by ID.
    """
    user = crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail="The user with this ID does not exist in the system."
        )
    if user.id == current_user.id:
        return user
    # Assuming superuser can view any profile
    # if not current_user.is_superuser:
    #     raise HTTPException(status_code=400, detail="Not enough permissions")
    return user
