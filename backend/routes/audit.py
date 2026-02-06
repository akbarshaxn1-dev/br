from fastapi import APIRouter, Depends, HTTPException, status, Query
from routes.auth import get_current_user
from database import get_db
from models import AuditLogResponse
from utils.permissions import Permissions
from utils.audit import get_audit_logs
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get audit logs (admin only)"""
    # Check permission
    if not Permissions.can_view_audit_logs(current_user['role']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view audit logs"
        )
    
    logs = await get_audit_logs(
        skip=skip,
        limit=limit,
        user_id=user_id,
        resource_type=resource_type,
        action=action
    )
    
    return logs
