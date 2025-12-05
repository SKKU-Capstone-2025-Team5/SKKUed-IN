
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.notification import Notification, NotificationType
from app.schemas.notification import NotificationCreate, NotificationUpdate

def create_notification(db: Session, notification_in: NotificationCreate) -> Notification:
    """Create a new notification."""
    db_notification = Notification(
        user_id=notification_in.user_id,
        type=notification_in.type,
        entity_type=notification_in.entity_type,
        entity_id=notification_in.entity_id,
        message=notification_in.message,
        expires_at=notification_in.expires_at,
        deep_link=notification_in.deep_link,
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    """Get a single notification by its ID."""
    return db.query(Notification).filter(Notification.id == notification_id).first()

def get_user_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    is_read: Optional[bool] = None,
) -> List[Notification]:
    """Get all notifications for a user, with optional filtering by read status."""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    return query.offset(skip).limit(limit).all()

def update_notification(db: Session, notification: Notification, notification_in: NotificationUpdate) -> Notification:
    """Update a notification's details (e.g., mark as read)."""
    update_data = notification_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notification, field, value)
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def delete_notification(db: Session, notification_id: int) -> None:
    """Delete a notification."""
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if db_notification:
        db.delete(db_notification)
        db.commit()
