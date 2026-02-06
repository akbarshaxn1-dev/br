import socketio
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)

# Create Socket.IO server with CORS
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False
)

# Store active connections: {user_id: set of sids}
connections: Dict[str, Set[str]] = {}

# Store faction subscriptions: {faction_code: set of sids}
faction_rooms: Dict[str, Set[str]] = {}

@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    return True

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")
    
    # Remove from all connections
    for user_id, sids in connections.items():
        if sid in sids:
            sids.remove(sid)
    
    # Remove from faction rooms
    for faction_code, sids in faction_rooms.items():
        if sid in sids:
            sids.remove(sid)

@sio.event
async def authenticate(sid, data):
    """Authenticate user and store connection"""
    user_id = data.get('user_id')
    faction = data.get('faction')
    
    if not user_id:
        await sio.emit('error', {'message': 'User ID required'}, room=sid)
        return
    
    # Store connection
    if user_id not in connections:
        connections[user_id] = set()
    connections[user_id].add(sid)
    
    # Join faction room if provided
    if faction:
        if faction not in faction_rooms:
            faction_rooms[faction] = set()
        faction_rooms[faction].add(sid)
        await sio.enter_room(sid, f"faction_{faction}")
    
    logger.info(f"User {user_id} authenticated on sid {sid}")
    await sio.emit('authenticated', {'user_id': user_id}, room=sid)

@sio.event
async def join_department(sid, data):
    """Join department room for real-time updates"""
    department_id = data.get('department_id')
    if department_id:
        await sio.enter_room(sid, f"department_{department_id}")
        logger.info(f"Client {sid} joined department {department_id}")

@sio.event
async def leave_department(sid, data):
    """Leave department room"""
    department_id = data.get('department_id')
    if department_id:
        await sio.leave_room(sid, f"department_{department_id}")
        logger.info(f"Client {sid} left department {department_id}")

# Broadcast functions
async def broadcast_table_update(department_id: str, week_id: str, updated_by: str):
    """Broadcast table update to all users in department"""
    await sio.emit(
        'table_updated',
        {
            'department_id': department_id,
            'week_id': week_id,
            'updated_by': updated_by
        },
        room=f"department_{department_id}"
    )
    logger.info(f"Broadcasted table update for department {department_id}")

async def broadcast_structure_change(department_id: str, updated_by: str):
    """Broadcast table structure change"""
    await sio.emit(
        'structure_changed',
        {
            'department_id': department_id,
            'updated_by': updated_by
        },
        room=f"department_{department_id}"
    )
    logger.info(f"Broadcasted structure change for department {department_id}")

async def send_notification(user_id: str, notification: dict):
    """Send notification to specific user"""
    if user_id in connections:
        for sid in connections[user_id]:
            await sio.emit('notification', notification, room=sid)
        logger.info(f"Sent notification to user {user_id}")

async def broadcast_to_faction(faction_code: str, event: str, data: dict):
    """Broadcast event to all users in a faction"""
    await sio.emit(event, data, room=f"faction_{faction_code}")
    logger.info(f"Broadcasted {event} to faction {faction_code}")
