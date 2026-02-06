from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from database import get_db
from models import (
    UserResponse, AdminUserCreate, UserUpdate, RoleEnum, FactionEnum
)
from utils.security import get_current_user, get_password_hash
from utils.permissions import Permissions
from utils.audit import log_action

router = APIRouter(prefix="/admin", tags=["admin"])

# Role display names
ROLE_NAMES = {
    "developer": "Разработчик",
    "gs": "Главный Следящий (ГС)",
    "zgs": "Заместитель ГС (ЗГС)",
    "leader_gov": "Лидер Правительства",
    "leader_fsb": "Лидер ФСБ",
    "leader_gibdd": "Лидер ГИБДД",
    "leader_umvd": "Лидер УМВД",
    "leader_army": "Лидер Армии",
    "leader_hospital": "Лидер Больницы",
    "leader_smi": "Лидер СМИ",
    "leader_fsin": "Лидер ФСИН",
    "head_of_department": "Начальник отдела",
    "deputy_head": "Заместитель начальника"
}

FACTION_NAMES = {
    "gov": "Правительство",
    "fsb": "ФСБ",
    "gibdd": "ГИБДД",
    "umvd": "УМВД",
    "army": "Армия",
    "hospital": "Больница",
    "smi": "СМИ",
    "fsin": "ФСИН"
}

def check_admin_access(current_user: dict):
    """Check if user has admin access"""
    if not Permissions.can_manage_users(current_user['role']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён. Требуются права администратора."
        )

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    faction: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all users (admin only)"""
    check_admin_access(current_user)
    
    db = get_db()
    
    # Build query
    query = {}
    if faction:
        query['faction'] = faction
    if role:
        query['role'] = role
    if is_active is not None:
        query['is_active'] = is_active
    
    users = await db.users.find(query, {'_id': 0, 'password_hash': 0}).to_list(1000)
    
    # Convert datetime strings to datetime objects
    for user in users:
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
    
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific user by ID (admin only)"""
    check_admin_access(current_user)
    
    db = get_db()
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'password_hash': 0})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    if isinstance(user.get('created_at'), str):
        user['created_at'] = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
    
    return user

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: AdminUserCreate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Create new user (admin only)"""
    check_admin_access(current_user)
    
    db = get_db()
    
    # Check if email already exists
    existing = await db.users.find_one({'email': user_data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Check if nickname already exists
    existing_nick = await db.users.find_one({'nickname': user_data.nickname})
    if existing_nick:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким ником уже существует"
        )
    
    # Validate faction for faction-specific roles
    if user_data.role in [RoleEnum.HEAD_OF_DEPARTMENT, RoleEnum.DEPUTY_HEAD]:
        if not user_data.faction or not user_data.department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для начальника/заместителя отдела необходимо указать фракцию и отдел"
            )
    
    if user_data.role.startswith('leader_'):
        # Extract faction from role
        faction_code = user_data.role.replace('leader_', '')
        user_data.faction = faction_code
    
    # Create user document
    now = datetime.now(timezone.utc)
    user_doc = {
        'id': str(uuid.uuid4()),
        'email': user_data.email,
        'password_hash': get_password_hash(user_data.password),
        'full_name': user_data.full_name,
        'nickname': user_data.nickname,
        'position': user_data.position,
        'vk_url': user_data.vk_url,
        'role': user_data.role,
        'faction': user_data.faction,
        'department_id': user_data.department_id,
        'is_active': True,
        'two_fa_enabled': False,
        'two_fa_secret': None,
        'created_at': now.isoformat(),
        'created_by': current_user['id']
    }
    
    await db.users.insert_one(user_doc)
    
    # Log action
    await log_action(
        db=db,
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="user_created",
        resource_type="user",
        resource_id=user_doc['id'],
        details={"nickname": user_data.nickname, "role": user_data.role},
        ip_address=request.client.host if request.client else None
    )
    
    # Return without password
    user_doc.pop('password_hash')
    user_doc.pop('two_fa_secret', None)
    user_doc['created_at'] = now
    
    return user_doc

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Update user (admin only)"""
    check_admin_access(current_user)
    
    db = get_db()
    
    # Find user
    user = await db.users.find_one({'id': user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Prevent modifying developer if not developer
    if user['role'] == 'developer' and current_user['role'] != 'developer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нельзя изменять аккаунт разработчика"
        )
    
    # Build update document
    update_data = {}
    old_values = {}
    
    for field, value in user_data.model_dump(exclude_unset=True).items():
        if value is not None:
            old_values[field] = user.get(field)
            update_data[field] = value
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет данных для обновления"
        )
    
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.users.update_one({'id': user_id}, {'$set': update_data})
    
    # Log action
    await log_action(
        db=db,
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="user_updated",
        resource_type="user",
        resource_id=user_id,
        details={"old_values": old_values, "new_values": update_data},
        ip_address=request.client.host if request.client else None
    )
    
    # Return updated user
    updated_user = await db.users.find_one({'id': user_id}, {'_id': 0, 'password_hash': 0, 'two_fa_secret': 0})
    if isinstance(updated_user.get('created_at'), str):
        updated_user['created_at'] = datetime.fromisoformat(updated_user['created_at'].replace('Z', '+00:00'))
    
    return updated_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Delete user (admin only) - soft delete"""
    check_admin_access(current_user)
    
    db = get_db()
    
    # Find user
    user = await db.users.find_one({'id': user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Prevent deleting developer
    if user['role'] == 'developer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нельзя удалить аккаунт разработчика"
        )
    
    # Prevent self-delete
    if user_id == current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить свой аккаунт"
        )
    
    # Soft delete - deactivate user
    await db.users.update_one(
        {'id': user_id},
        {'$set': {
            'is_active': False,
            'deleted_at': datetime.now(timezone.utc).isoformat(),
            'deleted_by': current_user['id']
        }}
    )
    
    # Store in deleted_users for recovery
    user['deleted_at'] = datetime.now(timezone.utc).isoformat()
    user['deleted_by'] = current_user['id']
    await db.deleted_users.insert_one(user)
    
    # Log action
    await log_action(
        db=db,
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="user_deleted",
        resource_type="user",
        resource_id=user_id,
        details={"nickname": user.get('nickname'), "email": user['email']},
        ip_address=request.client.host if request.client else None
    )
    
    return {"message": "Пользователь деактивирован"}

@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Activate/restore user (admin only)"""
    check_admin_access(current_user)
    
    db = get_db()
    
    user = await db.users.find_one({'id': user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    await db.users.update_one(
        {'id': user_id},
        {'$set': {'is_active': True}, '$unset': {'deleted_at': '', 'deleted_by': ''}}
    )
    
    # Log action
    await log_action(
        db=db,
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="user_activated",
        resource_type="user",
        resource_id=user_id,
        details={},
        ip_address=request.client.host if request.client else None
    )
    
    return {"message": "Пользователь активирован"}

@router.get("/roles")
async def get_roles(current_user: dict = Depends(get_current_user)):
    """Get list of available roles"""
    check_admin_access(current_user)
    
    roles = []
    for role in RoleEnum:
        roles.append({
            "value": role.value,
            "label": ROLE_NAMES.get(role.value, role.value)
        })
    
    return roles

@router.get("/factions-list")
async def get_factions_list(current_user: dict = Depends(get_current_user)):
    """Get list of available factions"""
    check_admin_access(current_user)
    
    factions = []
    for faction in FactionEnum:
        factions.append({
            "value": faction.value,
            "label": FACTION_NAMES.get(faction.value, faction.value)
        })
    
    return factions

@router.get("/departments-list")
async def get_departments_list(
    faction: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get list of departments for dropdown"""
    check_admin_access(current_user)
    
    db = get_db()
    
    query = {}
    if faction:
        # Get faction ID
        faction_doc = await db.factions.find_one({'code': faction})
        if faction_doc:
            query['faction_id'] = faction_doc['id']
    
    departments = await db.departments.find(query, {'_id': 0, 'id': 1, 'name': 1, 'faction_id': 1}).to_list(500)
    
    return departments

@router.get("/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """Get admin dashboard statistics"""
    check_admin_access(current_user)
    
    db = get_db()
    
    total_users = await db.users.count_documents({'is_active': True})
    total_departments = await db.departments.count_documents({})
    total_factions = await db.factions.count_documents({})
    
    # Users by role
    users_by_role = {}
    for role in RoleEnum:
        count = await db.users.count_documents({'role': role.value, 'is_active': True})
        if count > 0:
            users_by_role[ROLE_NAMES.get(role.value, role.value)] = count
    
    # Users by faction
    users_by_faction = {}
    for faction in FactionEnum:
        count = await db.users.count_documents({'faction': faction.value, 'is_active': True})
        if count > 0:
            users_by_faction[FACTION_NAMES.get(faction.value, faction.value)] = count
    
    # Recent logins (last 24 hours)
    from datetime import timedelta
    day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    recent_logins = await db.audit_logs.count_documents({
        'action': 'user_login',
        'timestamp': {'$gte': day_ago}
    })
    
    return {
        "total_users": total_users,
        "total_departments": total_departments,
        "total_factions": total_factions,
        "users_by_role": users_by_role,
        "users_by_faction": users_by_faction,
        "recent_logins_24h": recent_logins
    }

@router.post("/impersonate/{user_id}")
async def impersonate_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Impersonate another user (developer only)"""
    if current_user['role'] != 'developer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только разработчик может имитировать пользователей"
        )
    
    db = get_db()
    
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0, 'password_hash': 0, 'two_fa_secret': 0})
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Log action
    await log_action(
        db=db,
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="user_impersonated",
        resource_type="user",
        resource_id=user_id,
        details={"target_email": target_user['email']},
        ip_address=request.client.host if request.client else None
    )
    
    # Generate new token for impersonated user
    from utils.security import create_access_token, create_refresh_token
    
    access_token = create_access_token(data={"user_id": target_user['id'], "impersonated_by": current_user['id']})
    refresh_token = create_refresh_token(data={"user_id": target_user['id']})
    
    if isinstance(target_user.get('created_at'), str):
        target_user['created_at'] = datetime.fromisoformat(target_user['created_at'].replace('Z', '+00:00'))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": target_user
    }
