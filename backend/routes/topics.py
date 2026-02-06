from fastapi import APIRouter, Depends, HTTPException, status
from routes.auth import get_current_user
from database import get_db
from models import LectureTopicCreate, LectureTopicResponse, TrainingTopicCreate, TrainingTopicResponse
from utils.permissions import Permissions
from utils.audit import log_action
from datetime import datetime
from typing import List
import uuid

router = APIRouter(prefix="/topics", tags=["topics"])

# Lecture Topics
@router.get("/lectures/faction/{faction_code}", response_model=List[LectureTopicResponse])
async def get_lecture_topics(faction_code: str, current_user: dict = Depends(get_current_user)):
    """Get lecture topics for a faction"""
    db = get_db()
    
    # Get faction
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    # Check permission
    if not Permissions.can_view_faction(current_user['role'], current_user.get('faction'), faction_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this faction's topics"
        )
    
    topics = await db.lecture_topics.find({"faction_id": faction['id']}, {"_id": 0}).sort("order", 1).to_list(100)
    
    # Convert datetime strings
    for topic in topics:
        if isinstance(topic.get('created_at'), str):
            topic['created_at'] = datetime.fromisoformat(topic['created_at'])
    
    return topics

@router.post("/lectures/faction/{faction_code}", response_model=LectureTopicResponse)
async def create_lecture_topic(faction_code: str, topic_data: LectureTopicCreate, current_user: dict = Depends(get_current_user)):
    """Create lecture topic"""
    db = get_db()
    
    # Get faction
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    # Check permission (only leaders and admins)
    if not (current_user['role'].startswith('leader_') or 
            current_user['role'] in ['developer', 'gs', 'zgs']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders can manage topics"
        )
    
    if current_user['role'].startswith('leader_') and current_user.get('faction') != faction_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage topics in your faction"
        )
    
    # Get next order if not provided
    if topic_data.order is None:
        last_topic = await db.lecture_topics.find_one(
            {"faction_id": faction['id']},
            {"_id": 0},
            sort=[("order", -1)]
        )
        topic_data.order = (last_topic['order'] + 1) if last_topic else 0
    
    # Create topic
    from models import LectureTopic
    topic_dict = topic_data.model_dump()
    topic_dict['faction_id'] = faction['id']
    
    topic = LectureTopic(**topic_dict)
    doc = topic.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.lecture_topics.insert_one(doc)
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="lecture_topic_created",
        resource_type="lecture_topic",
        resource_id=doc['id'],
        new_value={"topic": topic_data.topic, "faction": faction_code}
    )
    
    doc['created_at'] = datetime.fromisoformat(doc['created_at'])
    return doc

@router.delete("/lectures/{topic_id}")
async def delete_lecture_topic(topic_id: str, current_user: dict = Depends(get_current_user)):
    """Delete lecture topic"""
    db = get_db()
    
    # Get topic
    topic = await db.lecture_topics.find_one({"id": topic_id}, {"_id": 0})
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Get faction
    faction = await db.factions.find_one({"id": topic['faction_id']}, {"_id": 0})
    
    # Check permission
    if not (current_user['role'].startswith('leader_') or 
            current_user['role'] in ['developer', 'gs', 'zgs']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders can manage topics"
        )
    
    if current_user['role'].startswith('leader_') and current_user.get('faction') != faction['code']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage topics in your faction"
        )
    
    # Delete topic
    await db.lecture_topics.delete_one({"id": topic_id})
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="lecture_topic_deleted",
        resource_type="lecture_topic",
        resource_id=topic_id,
        old_value=topic
    )
    
    return {"message": "Lecture topic deleted successfully"}

# Training Topics
@router.get("/trainings/faction/{faction_code}", response_model=List[TrainingTopicResponse])
async def get_training_topics(faction_code: str, current_user: dict = Depends(get_current_user)):
    """Get training topics for a faction"""
    db = get_db()
    
    # Get faction
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    # Check permission
    if not Permissions.can_view_faction(current_user['role'], current_user.get('faction'), faction_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this faction's topics"
        )
    
    topics = await db.training_topics.find({"faction_id": faction['id']}, {"_id": 0}).sort("order", 1).to_list(100)
    
    # Convert datetime strings
    for topic in topics:
        if isinstance(topic.get('created_at'), str):
            topic['created_at'] = datetime.fromisoformat(topic['created_at'])
    
    return topics

@router.post("/trainings/faction/{faction_code}", response_model=TrainingTopicResponse)
async def create_training_topic(faction_code: str, topic_data: TrainingTopicCreate, current_user: dict = Depends(get_current_user)):
    """Create training topic"""
    db = get_db()
    
    # Get faction
    faction = await db.factions.find_one({"code": faction_code}, {"_id": 0})
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    # Check permission
    if not (current_user['role'].startswith('leader_') or 
            current_user['role'] in ['developer', 'gs', 'zgs']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders can manage topics"
        )
    
    if current_user['role'].startswith('leader_') and current_user.get('faction') != faction_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage topics in your faction"
        )
    
    # Get next order if not provided
    if topic_data.order is None:
        last_topic = await db.training_topics.find_one(
            {"faction_id": faction['id']},
            {"_id": 0},
            sort=[("order", -1)]
        )
        topic_data.order = (last_topic['order'] + 1) if last_topic else 0
    
    # Create topic
    from models import TrainingTopic
    topic_dict = topic_data.model_dump()
    topic_dict['faction_id'] = faction['id']
    
    topic = TrainingTopic(**topic_dict)
    doc = topic.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.training_topics.insert_one(doc)
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="training_topic_created",
        resource_type="training_topic",
        resource_id=doc['id'],
        new_value={"topic": topic_data.topic, "faction": faction_code}
    )
    
    doc['created_at'] = datetime.fromisoformat(doc['created_at'])
    return doc

@router.delete("/trainings/{topic_id}")
async def delete_training_topic(topic_id: str, current_user: dict = Depends(get_current_user)):
    """Delete training topic"""
    db = get_db()
    
    # Get topic
    topic = await db.training_topics.find_one({"id": topic_id}, {"_id": 0})
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Get faction
    faction = await db.factions.find_one({"id": topic['faction_id']}, {"_id": 0})
    
    # Check permission
    if not (current_user['role'].startswith('leader_') or 
            current_user['role'] in ['developer', 'gs', 'zgs']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders can manage topics"
        )
    
    if current_user['role'].startswith('leader_') and current_user.get('faction') != faction['code']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage topics in your faction"
        )
    
    # Delete topic
    await db.training_topics.delete_one({"id": topic_id})
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="training_topic_deleted",
        resource_type="training_topic",
        resource_id=topic_id,
        old_value=topic
    )
    
    return {"message": "Training topic deleted successfully"}
