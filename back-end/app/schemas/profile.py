from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class ProfileBase(BaseModel):
    major: Optional[str] = Field(None, max_length=255)
    age: Optional[str] = Field(None, max_length=50)
<<<<<<< HEAD
    phone_number: Optional[EmailStr | str] = None #email or phone num. 
=======
    phone_number: Optional[EmailStr | str] = None
>>>>>>> e48c847f6748f33bd2ff9a8aa655ed5532ebd4b8
    introduction: Optional[str] = Field(None, max_length=1000)
    profile_image_url: Optional[str] = None
    core_skill_tags: Optional[List[str]] = Field(None, max_items=30)
    interests: Optional[List[str]] = Field(None, max_items=30)
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
