from datetime import datetime, timezone
from database import get_db
from models import AuditLog
from typing import Optional, Dict, Any

async def log_action(
    user_id: str,
    user_email: str,
    action: str,
    resource_type: str,
    resource_id: str,
    old_value: Optional[Dict[str, Any]] = None,
    new_value: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log an action to the audit log"""
    db = get_db()
    
    log_entry = AuditLog(
        user_id=user_id,
        user_email=user_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    doc = log_entry.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.audit_logs.insert_one(doc)

async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Retrieve audit logs with filters"""
    db = get_db()
    
    query = {}
    if user_id:
        query['user_id'] = user_id
    if resource_type:
        query['resource_type'] = resource_type
    if action:
        query['action'] = action
    if start_date or end_date:
        query['timestamp'] = {}
        if start_date:
            query['timestamp']['$gte'] = start_date.isoformat()
        if end_date:
            query['timestamp']['$lte'] = end_date.isoformat()
    
    logs = await db.audit_logs.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    # Convert ISO strings to datetime
    for log in logs:
        if isinstance(log['timestamp'], str):
            log['timestamp'] = datetime.fromisoformat(log['timestamp'])
    
    return logs
