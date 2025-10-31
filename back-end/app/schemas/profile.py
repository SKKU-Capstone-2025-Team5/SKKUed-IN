from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import List, Optional, Dict, Any

class ProfileBase(BaseModel):
    major: Optional[str] = Field(None, max_length=255)
    age: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[EmailStr | str] = None #email or phone num. 
    introduction: Optional[str] = Field(None, max_length=1000)
    profile_image_url: Optional[HttpUrl] = None

    core_skill_tags: Optional[List[str]] = Field(None, max_items=30)
    interests: Optional[List[str]] = Field(None, max_items=30)
    links: Optional[List[Link]] = Field(None, max_items=5)

    phone_number_public: Optional[bool] = False
    age_public: Optional[bool] = False

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileInDBBase(ProfileBase):
    id: int

    class Config:
        from_attributes = True

class Profile(ProfileInDBBase):
    pass