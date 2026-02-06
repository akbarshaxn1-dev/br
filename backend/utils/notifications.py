from database import get_db
from models import Notification, NotificationTypeEnum
from typing import List
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    async def create_notification(
        user_id: str,
        notification_type: NotificationTypeEnum,
        title: str,
        message: str
    ):
        """Create a new notification for a user"""
        db = get_db()
        
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message
        )
        
        doc = notification.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await db.notifications.insert_one(doc)
        logger.info(f"Notification created for user {user_id}: {title}")
        
        return notification
    
    @staticmethod
    async def get_user_notifications(user_id: str, unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user"""
        db = get_db()
        
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
        
        notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
        
        # Convert ISO strings to datetime
        for notif in notifications:
            if isinstance(notif['created_at'], str):
                notif['created_at'] = datetime.fromisoformat(notif['created_at'])
        
        return notifications
    
    @staticmethod
    async def mark_as_read(notification_id: str, user_id: str):
        """Mark a notification as read"""
        db = get_db()
        
        result = await db.notifications.update_one(
            {"id": notification_id, "user_id": user_id},
            {"$set": {"read": True}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def mark_all_as_read(user_id: str):
        """Mark all notifications as read for a user"""
        db = get_db()
        
        result = await db.notifications.update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True}}
        )
        
        return result.modified_count

from datetime import datetime
