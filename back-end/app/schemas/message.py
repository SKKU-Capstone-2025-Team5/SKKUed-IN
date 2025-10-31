import datetime
import enum
from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from app.models.message import ConversationType

# Forward declaration for UserReadForMessage to avoid circular imports
class UserReadForMessage(BaseModel):
    id: int
    full_name: Optional[str] = None
    profile_image_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    file_url: Optional[HttpUrl] = None 
    reply_to_message_id: Optional[int] = None 

class MessageCreate(MessageBase):
    conversation_id: int

class MessageRead(MessageBase):
    id: int
    created_at: datetime.datetime
    sender: UserReadForMessage 
    conversation_id: int
    read_by: List[int] = [] 

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    type: ConversationType

class ConversationCreate(ConversationBase):
    participant_ids: Optional[List[int]] = None
    team_id: Optional[int] = None

class ConversationRead(ConversationBase):
    id: int
    created_at: datetime.datetime
    participants: List[UserReadForMessage] 
    latest_message: Optional[MessageRead] = None
    unread_count: int = 0 

    class Config:
        from_attributes = True
