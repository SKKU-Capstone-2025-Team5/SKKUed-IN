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
    file_url: Optional[HttpUrl] = None # For file attachments
    reply_to_message_id: Optional[int] = None # For threading

class MessageCreate(MessageBase):
    conversation_id: int
    # sender_id will be set by the backend based on the authenticated user

class MessageRead(MessageBase):
    id: int
    created_at: datetime.datetime
    sender: UserReadForMessage # Nested schema for sender
    conversation_id: int
    read_by: List[int] = [] # List of user IDs who have read the message

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    type: ConversationType

class ConversationCreate(ConversationBase):
    # For DMs, list of user IDs to include (usually 2)
    participant_ids: Optional[List[int]] = None
    # For team chats, the team ID
    team_id: Optional[int] = None # Assuming a Team model exists or will exist

class ConversationRead(ConversationBase):
    id: int
    created_at: datetime.datetime
    participants: List[UserReadForMessage] # Nested schema for participants
    latest_message: Optional[MessageRead] = None # Latest message in the conversation
    unread_count: int = 0 # Number of unread messages for the current user

    class Config:
        from_attributes = True
