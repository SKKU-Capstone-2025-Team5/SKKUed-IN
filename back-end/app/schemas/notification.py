
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.notification import NotificationType

class NotificationBase(BaseModel):
    type: NotificationType
    entity_type: str
    entity_id: int
    message: str
    deep_link: Optional[str] = None

class NotificationCreate(NotificationBase):
    user_id: int
    expires_at: Optional[datetime] = None

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationRead(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
