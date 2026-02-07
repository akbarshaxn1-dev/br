from fastapi import APIRouter, Depends, HTTPException, status
from routes.auth import get_current_user
from database import get_db
from models import WeekResponse, TableDataUpdate
from utils.permissions import Permissions
from utils.audit import log_action
from utils.weeks import get_week_boundaries, format_week_label
from datetime import datetime, timezone
from typing import List
import uuid

router = APIRouter(prefix="/weeks", tags=["weeks"])

@router.get("/department/{department_id}", response_model=List[WeekResponse])
async def get_department_weeks(department_id: str, current_user: dict = Depends(get_current_user)):
    """Get all weeks for a department"""
    db = get_db()
    
    # Get department
    department = await db.departments.find_one({"id": department_id}, {"_id": 0})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Get faction
    faction = await db.factions.find_one({"id": department['faction_id']}, {"_id": 0})
    
    # Check permission
    if not Permissions.can_view_faction(current_user['role'], current_user.get('faction'), faction['code']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this department's weeks"
        )
    
    weeks = await db.weeks.find({"department_id": department_id}, {"_id": 0}).sort("week_start", -1).to_list(100)
    
    # Convert datetime strings
    for week in weeks:
        if isinstance(week.get('week_start'), str):
            week['week_start'] = datetime.fromisoformat(week['week_start'])
        if isinstance(week.get('week_end'), str):
            week['week_end'] = datetime.fromisoformat(week['week_end'])
        if isinstance(week.get('created_at'), str):
            week['created_at'] = datetime.fromisoformat(week['created_at'])
    
    return weeks

@router.get("/department/{department_id}/current", response_model=WeekResponse)
async def get_current_week(department_id: str, current_user: dict = Depends(get_current_user)):
    """Get or create current week for department"""
    db = get_db()
    
    # Get department
    department = await db.departments.find_one({"id": department_id}, {"_id": 0})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Get faction
    faction = await db.factions.find_one({"id": department['faction_id']}, {"_id": 0})
    
    # Check permission
    if not Permissions.can_view_faction(current_user['role'], current_user.get('faction'), faction['code']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this department's weeks"
        )
    
    # Get week boundaries
    monday, sunday = get_week_boundaries()
    
    # Check if current week exists
    week = await db.weeks.find_one(
        {
            "department_id": department_id,
            "week_start": monday.isoformat()
        },
        {"_id": 0}
    )
    
    if not week:
        # Create new week
        from models import WeekBase
        week_obj = WeekBase(
            department_id=department_id,
            week_start=monday,
            week_end=sunday,
            is_current=True
        )
        
        # Mark all previous weeks as not current
        await db.weeks.update_many(
            {"department_id": department_id},
            {"$set": {"is_current": False}}
        )
        
        week_doc = week_obj.model_dump()
        week_doc['week_start'] = week_doc['week_start'].isoformat()
        week_doc['week_end'] = week_doc['week_end'].isoformat()
        week_doc['created_at'] = week_doc['created_at'].isoformat()
        
        await db.weeks.insert_one(week_doc)
        
        # Create empty table data
        from models import TableData
        table_data = TableData(
            week_id=week_doc['id'],
            department_id=department_id,
            rows=[]
        )
        
        table_doc = table_data.model_dump()
        table_doc['created_at'] = table_doc['created_at'].isoformat()
        table_doc['updated_at'] = table_doc['updated_at'].isoformat()
        
        await db.table_data.insert_one(table_doc)
        
        # Log action
        await log_action(
            user_id=current_user['id'],
            user_email=current_user['email'],
            action="week_created",
            resource_type="week",
            resource_id=week_doc['id']
        )
        
        week = week_doc
    
    # Convert datetime strings
    if isinstance(week.get('week_start'), str):
        week['week_start'] = datetime.fromisoformat(week['week_start'])
    if isinstance(week.get('week_end'), str):
        week['week_end'] = datetime.fromisoformat(week['week_end'])
    if isinstance(week.get('created_at'), str):
        week['created_at'] = datetime.fromisoformat(week['created_at'])
    
    return week

@router.get("/{week_id}/table-data")
async def get_week_table_data(week_id: str, current_user: dict = Depends(get_current_user)):
    """Get table data for a specific week"""
    db = get_db()
    
    # Get week
    week = await db.weeks.find_one({"id": week_id}, {"_id": 0})
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found"
        )
    
    # Get department and faction for permission check
    department = await db.departments.find_one({"id": week['department_id']}, {"_id": 0})
    faction = await db.factions.find_one({"id": department['faction_id']}, {"_id": 0})
    
    # Check permission
    if not Permissions.can_view_faction(current_user['role'], current_user.get('faction'), faction['code']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this table data"
        )
    
    # Get table data
    table_data = await db.table_data.find_one({"week_id": week_id}, {"_id": 0})
    if not table_data:
        # Return empty structure
        return {"week_id": week_id, "rows": []}
    
    # Convert datetime strings
    if isinstance(table_data.get('created_at'), str):
        table_data['created_at'] = datetime.fromisoformat(table_data['created_at'])
    if isinstance(table_data.get('updated_at'), str):
        table_data['updated_at'] = datetime.fromisoformat(table_data['updated_at'])
    
    return table_data

@router.put("/{week_id}/table-data")
async def update_week_table_data(week_id: str, data: TableDataUpdate, current_user: dict = Depends(get_current_user)):
    """Update table data for a week"""
    db = get_db()
    
    # Get week
    week = await db.weeks.find_one({"id": week_id}, {"_id": 0})
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found"
        )
    
    # Get department and faction for permission check
    department = await db.departments.find_one({"id": week['department_id']}, {"_id": 0})
    faction = await db.factions.find_one({"id": department['faction_id']}, {"_id": 0})
    
    # Check permission
    if not Permissions.can_edit_table(
        current_user['role'],
        current_user.get('faction'),
        faction['code'],
        department['id'],
        current_user.get('department_id')
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this table"
        )
    
    # Get old data for audit log
    old_data = await db.table_data.find_one({"week_id": week_id}, {"_id": 0})
    
    # Update table data
    rows_data = [row.model_dump() for row in data.rows]
    
    result = await db.table_data.update_one(
        {"week_id": week_id},
        {
            "$set": {
                "rows": rows_data,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table data not found"
        )
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="table_data_updated",
        resource_type="table_data",
        resource_id=week_id,
        old_value={"rows_count": len(old_data.get('rows', [])) if old_data else 0},
        new_value={"rows_count": len(rows_data)}
    )
    
    # Broadcast via WebSocket
    try:
        from websocket_server import broadcast_table_update
        import asyncio
        asyncio.create_task(broadcast_table_update(
            department['id'], 
            week_id, 
            current_user.get('full_name', current_user['email'])
        ))
    except Exception as e:
        print(f"WebSocket broadcast error: {e}")
    
    return {"message": "Table data updated successfully"}
