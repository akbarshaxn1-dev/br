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


# Department-level topics (for department heads)
@router.get("/lectures/department/{department_id}", response_model=List[LectureTopicResponse])
async def get_department_lecture_topics(department_id: str, current_user: dict = Depends(get_current_user)):
    """Get lecture topics for a department (inherits from faction or custom)"""
    db = get_db()
    
    # Get department
    department = await db.departments.find_one({"id": department_id}, {"_id": 0})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check if department has custom topics
    custom_topics = await db.department_lecture_topics.find({"department_id": department_id}, {"_id": 0}).sort("order", 1).to_list(100)
    
    if custom_topics:
        for topic in custom_topics:
            if isinstance(topic.get('created_at'), str):
                topic['created_at'] = datetime.fromisoformat(topic['created_at'])
        return custom_topics
    
    # Otherwise return faction topics
    topics = await db.lecture_topics.find({"faction_id": department['faction_id']}, {"_id": 0}).sort("order", 1).to_list(100)
    
    for topic in topics:
        if isinstance(topic.get('created_at'), str):
            topic['created_at'] = datetime.fromisoformat(topic['created_at'])
    
    return topics

@router.post("/lectures/department/{department_id}", response_model=LectureTopicResponse)
async def create_department_lecture_topic(department_id: str, topic_data: LectureTopicCreate, current_user: dict = Depends(get_current_user)):
    """Create custom lecture topic for department (for department heads)"""
    db = get_db()
    
    # Get department
    department = await db.departments.find_one({"id": department_id}, {"_id": 0})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check permission - department heads and above
    can_manage = (
        current_user['role'] in ['developer', 'gs', 'zgs'] or
        current_user['role'].startswith('leader_') or
        (current_user['role'] == 'head_of_department' and current_user.get('department_id') == department_id)
    )
    
    if not can_manage:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage topics for this department"
        )
    
    # Get next order
    last_topic = await db.department_lecture_topics.find_one(
        {"department_id": department_id},
        {"_id": 0},
        sort=[("order", -1)]
    )
    order = (last_topic['order'] + 1) if last_topic else 0
    
    # Create topic
    from datetime import timezone
    topic_doc = {
        'id': str(uuid.uuid4()),
        'department_id': department_id,
        'faction_id': department['faction_id'],
        'topic': topic_data.topic,
        'order': order,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'created_by': current_user['id']
    }
    
    await db.department_lecture_topics.insert_one(topic_doc)
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="department_lecture_topic_created",
        resource_type="department_lecture_topic",
        resource_id=topic_doc['id'],
        new_value={"topic": topic_data.topic, "department_id": department_id}
    )
    
    topic_doc['created_at'] = datetime.fromisoformat(topic_doc['created_at'])
    return topic_doc

@router.delete("/lectures/department/{department_id}/{topic_id}")
async def delete_department_lecture_topic(department_id: str, topic_id: str, current_user: dict = Depends(get_current_user)):
    """Delete custom lecture topic for department"""
    db = get_db()
    
    # Get department
    department = await db.departments.find_one({"id": department_id}, {"_id": 0})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check permission
    can_manage = (
        current_user['role'] in ['developer', 'gs', 'zgs'] or
        current_user['role'].startswith('leader_') or
        (current_user['role'] == 'head_of_department' and current_user.get('department_id') == department_id)
    )
    
    if not can_manage:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage topics for this department"
        )
    
    # Delete topic
    result = await db.department_lecture_topics.delete_one({"id": topic_id, "department_id": department_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="department_lecture_topic_deleted",
        resource_type="department_lecture_topic",
        resource_id=topic_id
    )
    
    return {"message": "Topic deleted successfully"}

@router.get("/trainings/department/{department_id}", response_model=List[TrainingTopicResponse])
async def get_department_training_topics(department_id: str, current_user: dict = Depends(get_current_user)):
    """Get training topics for a department (inherits from faction or custom)"""
    db = get_db()
    
    # Get department
    department = await db.departments.find_one({"id": department_id}, {"_id": 0})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check if department has custom topics
    custom_topics = await db.department_training_topics.find({"department_id": department_id}, {"_id": 0}).sort("order", 1).to_list(100)
    
    if custom_topics:
        for topic in custom_topics:
            if isinstance(topic.get('created_at'), str):
                topic['created_at'] = datetime.fromisoformat(topic['created_at'])
        return custom_topics
    
    # Otherwise return faction topics
    topics = await db.training_topics.find({"faction_id": department['faction_id']}, {"_id": 0}).sort("order", 1).to_list(100)
    
    for topic in topics:
        if isinstance(topic.get('created_at'), str):
            topic['created_at'] = datetime.fromisoformat(topic['created_at'])
    
    return topics

@router.post("/trainings/department/{department_id}", response_model=TrainingTopicResponse)
async def create_department_training_topic(department_id: str, topic_data: TrainingTopicCreate, current_user: dict = Depends(get_current_user)):
    """Create custom training topic for department (for department heads)"""
    db = get_db()
    
    # Get department
    department = await db.departments.find_one({"id": department_id}, {"_id": 0})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check permission - department heads and above
    can_manage = (
        current_user['role'] in ['developer', 'gs', 'zgs'] or
        current_user['role'].startswith('leader_') or
        (current_user['role'] == 'head_of_department' and current_user.get('department_id') == department_id)
    )
    
    if not can_manage:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage topics for this department"
        )
    
    # Get next order
    last_topic = await db.department_training_topics.find_one(
        {"department_id": department_id},
        {"_id": 0},
        sort=[("order", -1)]
    )
    order = (last_topic['order'] + 1) if last_topic else 0
    
    # Create topic
    from datetime import timezone
    topic_doc = {
        'id': str(uuid.uuid4()),
        'department_id': department_id,
        'faction_id': department['faction_id'],
        'topic': topic_data.topic,
        'order': order,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'created_by': current_user['id']
    }
    
    await db.department_training_topics.insert_one(topic_doc)
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="department_training_topic_created",
        resource_type="department_training_topic",
        resource_id=topic_doc['id'],
        new_value={"topic": topic_data.topic, "department_id": department_id}
    )
    
    topic_doc['created_at'] = datetime.fromisoformat(topic_doc['created_at'])
    return topic_doc

@router.delete("/trainings/department/{department_id}/{topic_id}")
async def delete_department_training_topic(department_id: str, topic_id: str, current_user: dict = Depends(get_current_user)):
    """Delete custom training topic for department"""
    db = get_db()
    
    # Get department
    department = await db.departments.find_one({"id": department_id}, {"_id": 0})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check permission
    can_manage = (
        current_user['role'] in ['developer', 'gs', 'zgs'] or
        current_user['role'].startswith('leader_') or
        (current_user['role'] == 'head_of_department' and current_user.get('department_id') == department_id)
    )
    
    if not can_manage:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage topics for this department"
        )
    
    # Delete topic
    result = await db.department_training_topics.delete_one({"id": topic_id, "department_id": department_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Log action
    await log_action(
        user_id=current_user['id'],
        user_email=current_user['email'],
        action="department_training_topic_deleted",
        resource_type="department_training_topic",
        resource_id=topic_id
    )
    
    return {"message": "Topic deleted successfully"}

