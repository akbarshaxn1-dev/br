from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from config import config
import logging
from pathlib import Path
import socketio

# Import database
from database import connect_db, close_db

# Import routes
from routes import auth, factions, departments, weeks, topics, notifications, audit, admin

# Import WebSocket server
from websocket_server import sio

ROOT_DIR = Path(__file__).parent

# Create the main app
app = FastAPI(
    title="Единый Портал Управления Отделами",
    description="Enterprise Multi-Faction Management System",
    version="1.0.0"
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Include all routes
api_router.include_router(auth.router)
api_router.include_router(factions.router)
api_router.include_router(departments.router)
api_router.include_router(weeks.router)
api_router.include_router(topics.router)
api_router.include_router(notifications.router)
api_router.include_router(audit.router)
api_router.include_router(admin.router)

# Health check endpoint
@api_router.get("/")
async def root():
    return {
        "message": "Единый Портал Управления Отделами API",
        "version": "1.0.0",
        "status": "operational"
    }

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include the API router
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO
socket_app = socketio.ASGIApp(
    sio,
    other_asgi_app=app,
    socketio_path='/socket.io'
)

# Event handlers
@app.on_event("startup")
async def startup_db():
    await connect_db()
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_db():
    await close_db()
    logger.info("Application shutdown")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Export socket_app as the ASGI application
app = socket_app
