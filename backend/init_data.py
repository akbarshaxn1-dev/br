"""
Initialize database with default data:
- Super admin user (Vadim Smirnov)
- All 8 factions
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from utils.security import hash_password
from models import RoleEnum, FactionEnum
from datetime import datetime, timezone
import uuid

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

async def init_database():
    """Initialize database with default data"""
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    print("🚀 Initializing database...")
    
    # Initialize factions
    print("\n📋 Creating factions...")
    existing_factions = await db.factions.count_documents({})
    if existing_factions == 0:
        for faction_data in FACTIONS_DATA:
            faction_doc = {
                "id": str(uuid.uuid4()),
                "code": faction_data["code"],
                "name": faction_data["name"],
                "description": faction_data["description"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.factions.insert_one(faction_doc)
            print(f"✅ Created faction: {faction_data['name']}")
    else:
        print(f"ℹ️  Factions already exist ({existing_factions} factions)")
    
    # Create super admin
    print("\n👤 Creating super admin...")
    existing_admin = await db.users.find_one({"email": "vadim@emergent.dev"})
    if not existing_admin:
        admin_doc = {
            "id": str(uuid.uuid4()),
            "email": "vadim@emergent.dev",
            "password_hash": hash_password("admin123"),
            "full_name": "Vadim Smirnov",
            "vk_url": "https://vk.com/coder2406",
            "role": RoleEnum.DEVELOPER,
            "faction": None,
            "department_id": None,
            "is_active": True,
            "two_fa_enabled": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin_doc)
        print("✅ Super admin created")
        print("   Email: vadim@emergent.dev")
        print("   Password: admin123")
        print("   ⚠️  CHANGE PASSWORD AFTER FIRST LOGIN!")
    else:
        print("ℹ️  Super admin already exists")
    
    # Create example department for FSB (for demonstration)
    print("\n🏢 Creating example FSB department...")
    fsb_faction = await db.factions.find_one({"code": "fsb"}, {"_id": 0})
    if fsb_faction:
        existing_dept = await db.departments.find_one({"faction_id": fsb_faction['id']})
        if not existing_dept:
            dept_doc = {
                "id": str(uuid.uuid4()),
                "faction_id": fsb_faction['id'],
                "name": "Отдел контрразведки",
                "head_user_id": None,
                "deputy_user_ids": [],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.departments.insert_one(dept_doc)
            
            # Create default table structure
            default_columns = [
                {"id": str(uuid.uuid4()), "name": "Сотрудник", "type": "text", "order": 0, "editable": False},
                {"id": str(uuid.uuid4()), "name": "Пн", "type": "checkbox", "order": 1, "editable": True},
                {"id": str(uuid.uuid4()), "name": "Вт", "type": "checkbox", "order": 2, "editable": True},
                {"id": str(uuid.uuid4()), "name": "Ср", "type": "checkbox", "order": 3, "editable": True},
                {"id": str(uuid.uuid4()), "name": "Чт", "type": "checkbox", "order": 4, "editable": True},
                {"id": str(uuid.uuid4()), "name": "Пт", "type": "checkbox", "order": 5, "editable": True},
                {"id": str(uuid.uuid4()), "name": "Сб", "type": "checkbox", "order": 6, "editable": True},
                {"id": str(uuid.uuid4()), "name": "Вс", "type": "checkbox", "order": 7, "editable": True},
                {"id": str(uuid.uuid4()), "name": "Лекции", "type": "lecture", "order": 8, "editable": True},
                {"id": str(uuid.uuid4()), "name": "Тренировки", "type": "training", "order": 9, "editable": True},
            ]
            
            struct_doc = {
                "id": str(uuid.uuid4()),
                "department_id": dept_doc['id'],
                "columns": default_columns,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.table_structures.insert_one(struct_doc)
            
            print("✅ Example FSB department created")
        else:
            print("ℹ️  FSB department already exists")
    
    print("\n✅ Database initialization complete!")
    print("\n🔐 Login credentials:")
    print("   Email: vadim@emergent.dev")
    print("   Password: admin123")
    print("   Role: Developer (Super Admin)")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(init_database())
