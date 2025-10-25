from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
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
