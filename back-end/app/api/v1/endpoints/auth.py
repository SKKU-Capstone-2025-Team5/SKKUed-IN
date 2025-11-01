from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token

router = APIRouter()


@router.post("/register", response_model=schemas.User)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
):
    """
    Create new user.
    """
    user = crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    # Add SKKU email validation
    if not (user_in.email.endswith("@skku.edu") or user_in.email.endswith("@g.skku.edu")):
        raise HTTPException(
            status_code=400,
            detail="Only SKKU email addresses are allowed for registration.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.post("/login", response_model=schemas.Token)
def login_user(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud.user.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh_token():
    return {"message": "Token refresh endpoint"}


@router.post("/verify-email")
def verify_email():
    return {"message": "Email verification endpoint"}


@router.post("/logout")
def logout_user():
    return {"message": "User logout endpoint"}
