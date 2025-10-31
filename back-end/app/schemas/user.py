from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import List, Optional, Dict, Any
from app.schemas.team import TeamRead

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    major: Optional[str] = Field(None, max_length=255) 
    age: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    introduction: Optional[str] = Field(None, max_length=1000)
    profile_image_url: Optional[HttpUrl] = None

    core_skill_tags: Optional[List[str]] = Field(None, max_items=30) 
    interests: Optional[List[str]] = Field(None, max_items=30)

    phone_number_public: Optional[bool] = True 
    age_public: Optional[bool] = True 

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    teams: List[TeamRead] = []

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class UserUpdate(UserBase):
    password: Optional[str] = None