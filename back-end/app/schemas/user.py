from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from .skill import Skill
from .interest import Interest

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    major: Optional[str] = Field(None, max_length=255)
    age: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    introduction: Optional[str] = Field(None, max_length=1000)
    profile_image_url: Optional[str] = None
    core_skill_tags: Optional[List[str]] = Field(None, max_items=30)
    # interests: Optional[List[str]] = Field(None, max_items=30) # This was probably replaced by the relationship
    phone_number_public: Optional[bool] = True
    age_public: Optional[bool] = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    is_superuser: bool = False
    skills: Optional[List[str]] = []
    interests: Optional[List[str]] = []

class UserInDBBase(UserBase):
    id: Optional[int] = None
    class Config:
        from_attributes = True

    class Config:
        from_attributes = True




# Properties to return to client
class User(UserInDBBase):
    skills: List[Skill] = []
    interests: List[Interest] = []

# Properties stored in DB
class UserInDB(User):
    hashed_password: str

# Properties to receive via API on update
class UserUpdate(BaseModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    major: Optional[str] = Field(None, max_length=255)
    age: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    introduction: Optional[str] = Field(None, max_length=1000)
    profile_image_url: Optional[str] = None
    core_skill_tags: Optional[List[str]] = Field(None, max_items=30)
    interests: Optional[List[str]] = Field(None, max_items=30)
    phone_number_public: Optional[bool] = None
    age_public: Optional[bool] = None
