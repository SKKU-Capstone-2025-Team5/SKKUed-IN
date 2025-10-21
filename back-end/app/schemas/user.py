from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import List, Optional, Dict, Any

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    major: Optional[str] = Field(None, max_length=255) # Renamed from department
    age: Optional[str] = Field(None, max_length=50) # Renamed from grade_or_age
    phone_number: Optional[str] = Field(None, max_length=20)
    # phone_number: Optional[EmailStr | str] = None # Renamed from contact_info
    introduction: Optional[str] = Field(None, max_length=1000)
    profile_image_url: Optional[HttpUrl] = None

    core_skill_tags: Optional[List[str]] = Field(None, max_items=30) # Renamed from skills
    interests: Optional[List[str]] = Field(None, max_items=30)

    phone_number_public: Optional[bool] = True 
    age_public: Optional[bool] = True 

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to return to client
class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True # orm_mode = True for pydantic v1

# Properties stored in DB
class UserInDB(User):
    hashed_password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None