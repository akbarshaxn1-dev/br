from fastapi import APIRouter, Depends, HTTPException, status, Query
from routes.auth import get_current_user
from database import get_db
from models import FactionResponse, FactionEnum
from utils.permissions import Permissions
from utils.audit import log_action
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/factions", tags=["factions"])

# Faction definitions
FACTIONS_DATA = [
    {"code": "gov", "name": "Правительство", "description": "Центральный орган управления"},
    {"code": "fsb", "name": "ФСБ", "description": "Федеральная служба безопасности"},
    {"code": "gibdd", "name": "ГИБДД", "description": "Государственная инспекция безопасности дорожного движения"},
    {"code": "umvd", "name": "УМВД", "description": "Управление Министерства внутренних дел"},
    {"code": "army", "name": "Армия", "description": "Вооружённые силы"},
    {"code": "hospital", "name": "Больница", "description": "Медицинское учреждение"},
    {"code": "smi", "name": "СМИ", "description": "Средства массовой информации"},
    {"code": "fsin", "name": "ФСИН", "description": "Федеральная служба исполнения наказаний"},
]

@router.get("/", response_model=List[FactionResponse])
async def get_factions(current_user: dict = Depends(get_current_user)):
    """Get list of factions (filtered by user permissions)"""
    db = get_db()
    
    # Check if user can access all factions
    if Permissions.can_access_all_factions(current_user['role']):
        # Return all factions
        factions = await db.factions.find({}, {"_id": 0}).to_list(100)
    else:
        # Return only user's faction
        if not current_user.get('faction'):
            return []
        factions = await db.factions.find({"code": current_user['faction']}, {"_id": 0}).to_list(1)
    
    # Convert datetime strings
    for faction in factions:
        if isinstance(faction.get('created_at'), str):
            faction['created_at'] = datetime.fromisoformat(faction['created_at'])
    
    return factions

@router.get("/{faction_code}", response_model=FactionResponse)
async def get_faction(faction_code: str, current_user: dict = Depends(get_current_user)):
    """Get faction details"""
    db = get_db()
    
    # Check permission
    if not Permissions.can_view_faction(current_user['role'], current_user.get('faction'), faction_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this faction"
        )
    
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    if isinstance(faction.get('created_at'), str):
        faction['created_at'] = datetime.fromisoformat(faction['created_at'])
    
    return faction

@router.post("/initialize")
async def initialize_factions(current_user: dict = Depends(get_current_user)):
    """Initialize all factions (Developer only)"""
    db = get_db()
    
    if current_user['role'] != 'developer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only developers can initialize factions"
        )
    
    # Check if already initialized
    existing_count = await db.factions.count_documents({})
    if existing_count > 0:
        return {"message": f"Factions already initialized ({existing_count} factions exist)"}
    
    # Insert all factions
    from models import FactionBase
    for faction_data in FACTIONS_DATA:
        faction = FactionBase(**faction_data)
        doc = faction.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.factions.insert_one(doc)
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="factions_initialized",
        resource_type="faction",
        resource_id="all"
    )
    
    return {"message": f"Successfully initialized {len(FACTIONS_DATA)} factions"}
