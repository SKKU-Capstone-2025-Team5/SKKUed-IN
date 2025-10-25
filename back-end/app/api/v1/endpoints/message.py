from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.user import User
from app.models.message import Conversation # Import the model
from app.api.v1.endpoints.websocket import manager # New import
import json # Needed to serialize MessageRead to JSON

router = APIRouter()

@router.post("/conversations/", response_model=schemas.ConversationRead, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation_in: schemas.ConversationCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new conversation (DM or Team Chat).
    For DMs, ensures only one conversation exists between two users.
    """
    try:
        conversation = crud.message.create_conversation(db, conversation_in, current_user.id)
        return conversation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/conversations/", response_model=List[schemas.ConversationRead])
def read_conversations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all conversations for the current user.
    """
    conversations = crud.message.get_user_conversations(db, user_id=current_user.id)
    return conversations

@router.get("/conversations/{conversation_id}/messages", response_model=List[schemas.MessageRead])
def read_messages_in_conversation(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve messages for a specific conversation.
    """
    # Ensure current_user is a participant of the conversation
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation or current_user not in conversation.participants:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this conversation.")

    messages = crud.message.get_messages_in_conversation(db, conversation_id=conversation_id, skip=skip, limit=limit)
    return messages

@router.post("/conversations/{conversation_id}/messages", response_model=schemas.MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message( # Make it async
    conversation_id: int,
    message_in: schemas.MessageCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Send a new message to a conversation.
    """
    # Ensure current_user is a participant of the conversation
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation or current_user not in conversation.participants:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to send messages to this conversation.")
    
    message_in.conversation_id = conversation_id # Ensure conversation_id is set from path
    message = crud.message.create_message(db, message_in, sender_id=current_user.id)

    # Broadcast message to participants via WebSocket
    participant_ids = [p.id for p in conversation.participants]
    message_read_schema = schemas.MessageRead.model_validate(message) # Convert model to schema
    await manager.broadcast(json.dumps(message_read_schema.model_dump()), participant_ids) # Broadcast JSON string

    return message

@router.post("/messages/{message_id}/read", response_model=schemas.MessageRead)
def mark_message_as_read(
    message_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Mark a message as read by the current user.
    """
    message = crud.message.mark_message_as_read(db, message_id=message_id, user_id=current_user.id)
    if not message: # Check if message exists and was updated
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found.")
    return message