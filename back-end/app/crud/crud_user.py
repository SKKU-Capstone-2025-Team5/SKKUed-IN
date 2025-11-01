from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User, Skill, Interest
from app.schemas.user import UserCreate, UserBase, UserUpdate # Import UserBase for update
from typing import Any, Dict, Optional, Union, List

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create(db: Session, *, obj_in: UserCreate) -> User:
    db_obj = User(
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        is_superuser=obj_in.is_superuser,
        major=obj_in.major
    )

    if obj_in.skills:
        for skill_name in obj_in.skills:
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if not skill:
                skill = Skill(name=skill_name)
                db.add(skill)
            db_obj.skills.append(skill)

    if obj_in.interests:
        for interest_name in obj_in.interests:
            interest = db.query(Interest).filter(Interest.name == interest_name).first()
            if not interest:
                interest = Interest(name=interest_name)
                db.add(interest)
            db_obj.interests.append(interest)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def get_multi_by_ids(db: Session, *, ids: List[int]) -> List[User]:
    return db.query(User).filter(User.id.in_(ids)).all()

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
