from pydantic import BaseModel, EmailStr

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

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
