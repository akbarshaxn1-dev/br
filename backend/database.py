from motor.motor_asyncio import AsyncIOMotorClient
from config import config
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

async def connect_db():
    Database.client = AsyncIOMotorClient(config.MONGO_URL)
    Database.db = Database.client[config.DB_NAME]
    logger.info("Connected to MongoDB")
    
    # Create indexes
    await create_indexes()

async def close_db():
    if Database.client:
        Database.client.close()
        logger.info("Closed MongoDB connection")

async def create_indexes():
    """Create necessary database indexes for performance"""
    db = Database.db
    
    # Users indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")
    await db.users.create_index("faction")
    
    # Departments indexes
    await db.departments.create_index("faction_id")
    await db.departments.create_index(["faction_id", "name"])
    
    # Table structures indexes
    await db.table_structures.create_index("department_id", unique=True)
    
    # Weeks indexes
    await db.weeks.create_index("department_id")
    await db.weeks.create_index(["department_id", "week_start"])
    await db.weeks.create_index("is_current")
    
    # Table data indexes
    await db.table_data.create_index("week_id")
    await db.table_data.create_index("department_id")
    
    # Audit logs indexes
    await db.audit_logs.create_index("user_id")
    await db.audit_logs.create_index("timestamp")
    await db.audit_logs.create_index("resource_type")
    
    # Notifications indexes
    await db.notifications.create_index("user_id")
    await db.notifications.create_index(["user_id", "read"])
    
    # Refresh tokens indexes
    await db.refresh_tokens.create_index("token", unique=True)
    await db.refresh_tokens.create_index("user_id")
    await db.refresh_tokens.create_index("expires_at")
    
    logger.info("Database indexes created")

def get_db():
    return Database.db
