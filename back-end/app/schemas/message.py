import datetime
import enum
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, Field, computed_field
from pydantic_core import Url
from app.core.config import settings # Import settings

# Forward declaration for UserReadForMessage to avoid circular imports
class UserReadForMessage(BaseModel):
    id: int
    full_name: Optional[str] = None
    raw_profile_image_url: Optional[str] = Field(alias="profile_image_url", default=None) # Store original as string

    @computed_field
    @property
    def profile_image_url(self) -> Optional[Url]:
        if self.raw_profile_image_url:
            if self.raw_profile_image_url.startswith("http") or self.raw_profile_image_url.startswith("https"):
                return Url(self.raw_profile_image_url)
            return Url(f"{settings.BASE_URL}{self.raw_profile_image_url}")
        return None

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    file_url: Optional[HttpUrl] = None # For file attachments
    reply_to_message_id: Optional[int] = None # For threading

class MessageCreate(MessageBase):
    conversation_id: Optional[int] = None
    # sender_id will be set by the backend based on the authenticated user

class MessageRead(MessageBase):
    id: int
    created_at: datetime.datetime
    sender: UserReadForMessage # Nested schema for sender
    conversation_id: int
    read_by: List[int] = [] # List of user IDs who have read the message

    class Config:
        from_attributes = True

class ConversationType(str, enum.Enum):
    DM = "dm"
    TEAM = "team"

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
