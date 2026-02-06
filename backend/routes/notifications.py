from fastapi import APIRouter, Depends, HTTPException, status
from routes.auth import get_current_user
from database import get_db
from models import NotificationResponse
from utils.notifications import NotificationService
from datetime import datetime
from typing import List

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(unread_only: bool = False, current_user: dict = Depends(get_current_user)):
    """Get user notifications"""
    notifications = await NotificationService.get_user_notifications(
        user_id=current_user['id'],
        unread_only=unread_only
    )
    return notifications

@router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Mark notification as read"""
    success = await NotificationService.mark_as_read(notification_id, current_user['id'])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return {"message": "Notification marked as read"}

@router.post("/read-all")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read"""
    count = await NotificationService.mark_all_as_read(current_user['id'])
    return {"message": f"Marked {count} notifications as read"}
