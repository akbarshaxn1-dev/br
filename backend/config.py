import os
from datetime import timedelta

class Config:
    # MongoDB
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME = os.environ.get('DB_NAME', 'dept_management')
    
    # JWT
    JWT_SECRET = os.environ.get('JWT_SECRET', 'your-super-secret-key-change-in-production-2024')
    JWT_ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 30
    
    # Security
    BCRYPT_ROUNDS = 12
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Audit
    AUDIT_RETENTION_DAYS = 365
    
config = Config()
