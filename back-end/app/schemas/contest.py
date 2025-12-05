from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import date

class ContestBase(BaseModel):
    ex_name: str
    ex_link: HttpUrl
    ex_host: Optional[str] = None
    ex_image: Optional[HttpUrl] = None
    ex_start: Optional[date] = None
    ex_end: Optional[date] = None
    ex_flag: Optional[int] = None

class ContestCreate(ContestBase):
    pass

class ContestUpdate(ContestBase):
    pass

class Contest(ContestBase):
    id: int

    class Config:
        from_attributes = True