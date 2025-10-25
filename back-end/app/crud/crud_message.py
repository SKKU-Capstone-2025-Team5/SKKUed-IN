from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.message import Conversation, Message, ConversationType, conversation_participant_association
from app.models.user import User
from app.schemas.message import ConversationCreate, MessageCreate

class CRUDMessage:
    def get_conversation_by_participants(self, db: Session, user_ids: List[int]) -> Optional[Conversation]:
        # 해당 user_ids가 정확히 2개인지 확인 - 추가할라믄 더 추가해야함. 
        if len(user_ids) != 2:
            return None 

        dm_conversations = db.query(Conversation).filter(Conversation.type == ConversationType.DM).all()

        for conv in dm_conversations:
            participant_ids_in_conv = sorted([p.id for p in conv.participants])
            if participant_ids_in_conv == sorted(user_ids):
                return conv
        return None

    def create_conversation(self, db: Session, conversation_in: ConversationCreate, current_user_id: int) -> Conversation:
        if conversation_in.type == ConversationType.DM:
            # 2명인지 확인 
            if not conversation_in.participant_ids or len(conversation_in.participant_ids) != 2:
                raise ValueError("DM conversations must have exactly two participants.")
            
            # 같은 멤버로 이미 존재하는 대화방 있는지 확인
            existing_conv = self.get_conversation_by_participants(db, conversation_in.participant_ids)
            if existing_conv:
                return existing_conv 

            # current user가 참여자에 포함되어 있는지 확인
            if current_user_id not in conversation_in.participant_ids:
                raise ValueError("Current user must be a participant in the DM.")

            # 생성
            db_conversation = Conversation(type=conversation_in.type)
            db.add(db_conversation)
            db.flush() # Flush to get conversation ID

            # 추가 
            for user_id in conversation_in.participant_ids:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    db_conversation.participants.append(user)
                else:
                    raise ValueError(f"User with ID {user_id} not found.")
            
            db.commit()
            db.refresh(db_conversation)
            return db_conversation
        
        elif conversation_in.type == ConversationType.TEAM:
            if not conversation_in.team_id:
                raise ValueError("Team conversations require a team_id.")
            
            db_conversation = Conversation(type=conversation_in.type)
            db.add(db_conversation)
            db.flush()
            
            current_user = db.query(User).filter(User.id == current_user_id).first()
            if current_user:
                db_conversation.participants.append(current_user)
            
            db.commit()
            db.refresh(db_conversation)
            return db_conversation
        
        else:
            raise ValueError("Invalid conversation type.")

    def get_user_conversations(self, db: Session, user_id: int) -> List[dict]:
        conversations = db.query(Conversation).join(Conversation.participants).filter(User.id == user_id).all()

        result = []
        for conv in conversations:
            # 최신 메시지 가져오기 
            latest_message = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.desc()).first()

            # Calculate unread count ( sent / read 여부 기준 )
            unread_count = db.query(Message).filter(
                Message.conversation_id == conv.id,
                Message.sender_id != user_id, # Exclude messages sent by current user
                ~Message.read_by.contains(user_id) # Check if user_id is NOT in the read_by JSON array
            ).count()

            conv_data = {
                "id": conv.id,
                "type": conv.type,
                "created_at": conv.created_at,
                "participants": conv.participants, # Pydantic
                "latest_message": latest_message, # Pydantic
                "unread_count": unread_count,
            }
            result.append(conv_data)
        return result

    def get_messages_in_conversation(self, db: Session, conversation_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).offset(skip).limit(limit).all() # type: ignore

    def create_message(self, db: Session, message_in: MessageCreate, sender_id: int) -> Message:
        db_message = Message(
            content=message_in.content,
            sender_id=sender_id,
            conversation_id=message_in.conversation_id,
            file_url=str(message_in.file_url) if message_in.file_url else None,
            reply_to_message_id=message_in.reply_to_message_id,
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    def mark_message_as_read(self, db: Session, message_id: int, user_id: int) -> Optional[Message]:
        message = db.query(Message).filter(Message.id == message_id).first()
        if message and user_id not in message.read_by:
            message.read_by.append(user_id)
            db.add(message)
            db.commit()
            db.refresh(message)
        return message

crud_message = CRUDMessage()
