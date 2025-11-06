from sqlalchemy.orm import Session, selectinload

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.models.skill import Skill
from app.models.interest import Interest
from app.schemas.user import UserCreate, UserBase, UserUpdate # Import UserBase for update
from typing import Any, Dict, Optional, Union, List


    return db.query(User).options(selectinload(User.skills), selectinload(User.interests)).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create(db: Session, *, obj_in: UserCreate) -> User:
    default_profile_image = "/images/basic_profile.png"
    profile_image_to_use = obj_in.profile_image_url if obj_in.profile_image_url else default_profile_image


    db_obj = User(
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        is_superuser=obj_in.is_superuser,
        major=obj_in.major,
        profile_image_url=profile_image_to_use # Assign profile_image_url
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

def get_multi(db: Session, *, skip: int = 0, limit: Optional[int] = 100) -> List[User]:
    query = db.query(User).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    return query.all()

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

    # Handle skills update
    if "skills" in update_data:
        db_user.skills.clear() # Clear existing skills
        for skill_name in update_data["skills"]:
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if not skill:
                skill = Skill(name=skill_name)
                db.add(skill)
            db_user.skills.append(skill)
        del update_data["skills"]

    # Handle interests update
    if "interests" in update_data:
        db_user.interests.clear() # Clear existing interests
        for interest_name in update_data["interests"]:
            interest = db.query(Interest).filter(Interest.name == interest_name).first()
            if not interest:
                interest = Interest(name=interest_name)
                db.add(interest)
            db_user.interests.append(interest)
        del update_data["interests"]

    for field in update_data:
        if hasattr(db_user, field):
            setattr(db_user, field, update_data[field])

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def search_users(db: Session, query: str) -> List[User]:
    # First, try to find an exact match for full_name or email
    exact_match = db.query(User).filter(
        (User.full_name == query) | (User.email == query)
    ).first()

    if exact_match:
        return [exact_match]
    
    # If no exact match, fall back to partial, case-insensitive matching
    return db.query(User).filter(
        User.full_name.ilike(f"%{query}%") |
        User.email.ilike(f"%{query}%")
    ).all()
