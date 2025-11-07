from pydantic import BaseModel

class Interest(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
