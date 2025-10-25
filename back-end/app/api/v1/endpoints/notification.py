
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[schemas.NotificationRead])
def read_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
    is_read: Optional[bool] = None,
) -> Any:
    """
    Retrieve notifications for the current user.
    """
    notifications = crud.notification.get_user_notifications(
        db=db, user_id=current_user.id, skip=skip, limit=limit, is_read=is_read
    )
    return notifications

@router.put("/{notification_id}", response_model=schemas.NotificationRead)
def update_notification(
    notification_id: int,
    notification_in: schemas.NotificationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a notification (e.g., mark as read).
    """
    notification = crud.notification.get_notification(db, notification_id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    notification = crud.notification.update_notification(db=db, notification=notification, notification_in=notification_in)
    return notification
