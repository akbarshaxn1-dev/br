from fastapi import APIRouter, Depends, HTTPException, status
from routes.auth import get_current_user
from database import get_db
from models import DepartmentCreate, DepartmentResponse
from utils.permissions import Permissions
from utils.audit import log_action
from utils.notifications import NotificationService
from models import NotificationTypeEnum
from datetime import datetime
from typing import List
import uuid

router = APIRouter(prefix="/departments", tags=["departments"])

@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: str, current_user: dict = Depends(get_current_user)):
    """Get department by ID"""
    db = get_db()
    
    department = await db.departments.find_one({"id": department_id}, {"_id": 0})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Get faction info
    faction = await db.factions.find_one({"id": department['faction_id']}, {"_id": 0})
    
    # Check permission
    if faction and not Permissions.can_view_faction(current_user['role'], current_user.get('faction'), faction['code']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this department"
        )
    
    # Add faction_code for frontend convenience
    if faction:
        department['faction_code'] = faction['code']
    
    if isinstance(department.get('created_at'), str):
        department['created_at'] = datetime.fromisoformat(department['created_at'])
    
    return department

@router.get("/faction/{faction_code}", response_model=List[DepartmentResponse])
async def get_faction_departments(faction_code: str, current_user: dict = Depends(get_current_user)):
    """Get all departments for a faction"""
    db = get_db()
    
    # Check permission
    if not Permissions.can_view_faction(current_user['role'], current_user.get('faction'), faction_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this faction's departments"
        )
    
    # Get faction
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    departments = await db.departments.find({"faction_id": faction['id']}, {"_id": 0}).to_list(100)
    
    # Convert datetime strings
    for dept in departments:
        if isinstance(dept.get('created_at'), str):
            dept['created_at'] = datetime.fromisoformat(dept['created_at'])
    
    return departments

@router.post("/faction/{faction_code}", response_model=DepartmentResponse)
async def create_department(faction_code: str, department_data: DepartmentCreate, current_user: dict = Depends(get_current_user)):
    """Create a new department"""
    db = get_db()
    
    # Get faction
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    # Check permission
    if not Permissions.can_manage_department(
        current_user['role'], 
        current_user.get('faction'), 
        faction_code, 
        "",  # New department
        current_user.get('department_id')
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create departments in this faction"
        )
    
    # Create department
    from models import DepartmentBase
    dept_dict = department_data.model_dump()
    dept_dict['faction_id'] = faction['id']
    
    department = DepartmentBase(**dept_dict)
    doc = department.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.departments.insert_one(doc)
    
    # Create default table structure for the department
    from models import TableStructure, TableStructureColumn
    default_columns = [
        TableStructureColumn(name="Сотрудник", type="text", order=0, editable=False),
        TableStructureColumn(name="Пн", type="checkbox", order=1),
        TableStructureColumn(name="Вт", type="checkbox", order=2),
        TableStructureColumn(name="Ср", type="checkbox", order=3),
        TableStructureColumn(name="Чт", type="checkbox", order=4),
        TableStructureColumn(name="Пт", type="checkbox", order=5),
        TableStructureColumn(name="Сб", type="checkbox", order=6),
        TableStructureColumn(name="Вс", type="checkbox", order=7),
        TableStructureColumn(name="Лекции", type="lecture", order=8),
        TableStructureColumn(name="Тренировки", type="training", order=9),
    ]
    
    table_structure = TableStructure(department_id=doc['id'], columns=default_columns)
    struct_doc = table_structure.model_dump()
    struct_doc['created_at'] = struct_doc['created_at'].isoformat()
    struct_doc['updated_at'] = struct_doc['updated_at'].isoformat()
    
    await db.table_structures.insert_one(struct_doc)
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="department_created",
        resource_type="department",
        resource_id=doc['id'],
        new_value={"name": department_data.name, "faction": faction_code}
    )
    
    # Convert back datetime
    doc['created_at'] = datetime.fromisoformat(doc['created_at'])
    
    return doc

@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(department_id: str, department_data: DepartmentCreate, current_user: dict = Depends(get_current_user)):
    """Update department"""
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
    if not Permissions.can_manage_department(
        current_user['role'],
        current_user.get('faction'),
        faction['code'],
        department_id,
        current_user.get('department_id')
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this department"
        )
    
    # Update department
    update_data = department_data.model_dump(exclude_unset=True)
    
    await db.departments.update_one(
        {"id": department_id},
        {"$set": update_data}
    )
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="department_updated",
        resource_type="department",
        resource_id=department_id,
        old_value=department,
        new_value=update_data
    )
    
    # Get updated department
    updated_dept = await db.departments.find_one({"id": department_id}, {"_id": 0})
    if isinstance(updated_dept.get('created_at'), str):
        updated_dept['created_at'] = datetime.fromisoformat(updated_dept['created_at'])
    
    return updated_dept

@router.delete("/{department_id}")
async def delete_department(department_id: str, current_user: dict = Depends(get_current_user)):
    """Delete department"""
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
    if not Permissions.can_manage_department(
        current_user['role'],
        current_user.get('faction'),
        faction['code'],
        department_id,
        current_user.get('department_id')
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this department"
        )
    
    # Delete related data
    await db.table_structures.delete_many({"department_id": department_id})
    await db.weeks.delete_many({"department_id": department_id})
    await db.table_data.delete_many({"department_id": department_id})
    
    # Delete department
    await db.departments.delete_one({"id": department_id})
    
    # Notify affected users
    affected_users = await db.users.find({"department_id": department_id}, {"_id": 0}).to_list(100)
    for user in affected_users:
        await NotificationService.create_notification(
            user_id=user['id'],
            notification_type=NotificationTypeEnum.DEPARTMENT_DELETED,
            title="Отдел удалён",
            message=f"Отдел '{department['name']}' был удалён"
        )
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="department_deleted",
        resource_type="department",
        resource_id=department_id,
        old_value=department
    )
    
    return {"message": "Department deleted successfully"}
