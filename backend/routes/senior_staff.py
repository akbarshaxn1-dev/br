from fastapi import APIRouter, Depends, HTTPException, status
from routes.auth import get_current_user
from database import get_db
from models import SeniorStaffTable, SeniorStaffTableUpdate, SeniorStaffRow
from utils.permissions import Permissions
from utils.audit import log_action
from datetime import datetime, timezone
from typing import List
import uuid

router = APIRouter(prefix="/senior-staff", tags=["senior-staff"])

@router.get("/faction/{faction_code}")
async def get_senior_staff_table(faction_code: str, current_user: dict = Depends(get_current_user)):
    """Get senior staff table for a faction"""
    db = get_db()
    
    # Get faction
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    # Check permission - only leader of this faction, gs, zgs, or developer
    if not Permissions.can_manage_faction(current_user['role'], current_user.get('faction'), faction_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faction leader or higher can view senior staff table"
        )
    
    # Get or create senior staff table
    table = await db.senior_staff.find_one({"faction_id": faction['id']}, {"_id": 0})
    
    if not table:
        # Create new empty table
        new_table = SeniorStaffTable(
            faction_id=faction['id'],
            rows=[]
        )
        table_doc = new_table.model_dump()
        table_doc['created_at'] = table_doc['created_at'].isoformat()
        table_doc['updated_at'] = table_doc['updated_at'].isoformat()
        
        await db.senior_staff.insert_one(table_doc)
        table = table_doc
    
    # Convert datetime strings
    if isinstance(table.get('created_at'), str):
        table['created_at'] = datetime.fromisoformat(table['created_at'])
    if isinstance(table.get('updated_at'), str):
        table['updated_at'] = datetime.fromisoformat(table['updated_at'])
    
    return table

@router.put("/faction/{faction_code}")
async def update_senior_staff_table(
    faction_code: str, 
    data: SeniorStaffTableUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update senior staff table for a faction"""
    db = get_db()
    
    # Get faction
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    # Check permission - only leader of this faction, gs, zgs, or developer
    if not Permissions.can_manage_faction(current_user['role'], current_user.get('faction'), faction_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faction leader or higher can edit senior staff table"
        )
    
    # Get old data for audit
    old_table = await db.senior_staff.find_one({"faction_id": faction['id']}, {"_id": 0})
    
    # Prepare rows data
    rows_data = [row.model_dump() for row in data.rows]
    
    if old_table:
        # Update existing table
        result = await db.senior_staff.update_one(
            {"faction_id": faction['id']},
            {
                "$set": {
                    "rows": rows_data,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    else:
        # Create new table
        new_table = SeniorStaffTable(
            faction_id=faction['id'],
            rows=data.rows
        )
        table_doc = new_table.model_dump()
        table_doc['rows'] = rows_data
        table_doc['created_at'] = table_doc['created_at'].isoformat()
        table_doc['updated_at'] = table_doc['updated_at'].isoformat()
        
        await db.senior_staff.insert_one(table_doc)
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="senior_staff_updated",
        resource_type="senior_staff",
        resource_id=faction['id'],
        old_value={"rows_count": len(old_table.get('rows', [])) if old_table else 0},
        new_value={"rows_count": len(rows_data)}
    )
    
    return {"message": "Senior staff table updated successfully"}

@router.post("/faction/{faction_code}/row")
async def add_senior_staff_row(
    faction_code: str,
    row: SeniorStaffRow,
    current_user: dict = Depends(get_current_user)
):
    """Add a row to senior staff table"""
    db = get_db()
    
    # Get faction
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    # Check permission
    if not Permissions.can_manage_faction(current_user['role'], current_user.get('faction'), faction_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faction leader or higher can edit senior staff table"
        )
    
    # Get or create table
    table = await db.senior_staff.find_one({"faction_id": faction['id']}, {"_id": 0})
    
    row_data = row.model_dump()
    
    if table:
        # Add row to existing table
        await db.senior_staff.update_one(
            {"faction_id": faction['id']},
            {
                "$push": {"rows": row_data},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
    else:
        # Create new table with this row
        new_table = SeniorStaffTable(
            faction_id=faction['id'],
            rows=[row]
        )
        table_doc = new_table.model_dump()
        table_doc['rows'] = [row_data]
        table_doc['created_at'] = table_doc['created_at'].isoformat()
        table_doc['updated_at'] = table_doc['updated_at'].isoformat()
        
        await db.senior_staff.insert_one(table_doc)
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="senior_staff_row_added",
        resource_type="senior_staff",
        resource_id=faction['id'],
        new_value={"employee_name": row.employee_name}
    )
    
    return {"message": "Row added successfully"}

@router.delete("/faction/{faction_code}/row/{row_index}")
async def delete_senior_staff_row(
    faction_code: str,
    row_index: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a row from senior staff table"""
    db = get_db()
    
    # Get faction
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    # Check permission
    if not Permissions.can_manage_faction(current_user['role'], current_user.get('faction'), faction_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faction leader or higher can edit senior staff table"
        )
    
    # Get table
    table = await db.senior_staff.find_one({"faction_id": faction['id']}, {"_id": 0})
    if not table or row_index < 0 or row_index >= len(table.get('rows', [])):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Row not found"
        )
    
    # Get the row being deleted for audit
    deleted_row = table['rows'][row_index]
    
    # Remove the row
    rows = table.get('rows', [])
    rows.pop(row_index)
    
    await db.senior_staff.update_one(
        {"faction_id": faction['id']},
        {
            "$set": {
                "rows": rows,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="senior_staff_row_deleted",
        resource_type="senior_staff",
        resource_id=faction['id'],
        old_value={"employee_name": deleted_row.get('employee_name')}
    )
    
    return {"message": "Row deleted successfully"}
