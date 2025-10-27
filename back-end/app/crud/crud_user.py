from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserBase, UserUpdate # Import UserBase for update
from typing import Any, Dict, Optional, Union

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        major=user.major,
        age=user.age,
        phone_number=user.phone_number,
        introduction=user.introduction,
        profile_image_url=str(user.profile_image_url) if user.profile_image_url else None,
        core_skill_tags=user.core_skill_tags,
        interests=user.interests,
        phone_number_public=user.phone_number_public,
        age_public=user.age_public,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def update_user(
    db: Session,
    db_user: User,
    user_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    if isinstance(user_in, dict):
        update_data = user_in
    else:
        update_data = user_in.model_dump(exclude_unset=True) # Use model_dump for Pydantic v2

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    for field in update_data:
        if hasattr(db_user, field):
            setattr(db_user, field, update_data[field])

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
