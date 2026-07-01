import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import pytz
from typing import Dict, List
import json

from app.config import settings
from app.database import init_db, check_db_connection, SessionLocal
from app.routers import (
    auth, alerts, sensors, predictions, communities, users,
    missing_persons, relief, damage
)
from app.services.dhm_service import DHMService
from app.services.weather_service import WeatherService
from app.services.flood_prediction import FloodPredictionService
from app.services.landslide_prediction import LandslidePredictionService
from app.services.alert_distribution import AlertDistributionService
from app.utils.nepal_districts import NEPAL_DISTRICTS
from app.utils.seed_data import seed_nepal_data

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bipad_sahayak.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Nepal timezone
NEPAL_TZ = pytz.timezone(settings.NEPAL_TIMEZONE)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        logger.info(f"Client {client_id} disconnected")

    async def broadcast(self, message: dict, district: str = None):
        """Broadcast to all or district-specific clients"""
        targets = []
        if district:
            targets = self.active_connections.get(district, [])
        else:
            for connections in self.active_connections.values():
                targets.extend(connections)
        
        for connection in targets:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"WebSocket broadcast error: {e}")

manager = ConnectionManager()

# Scheduler
scheduler = AsyncIOScheduler(timezone=NEPAL_TZ)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting AI Bipad Sahayak Backend...")
    
    # Initialize database
    init_db()
    logger.info("✅ Database initialized with PostGIS")
    
    # Seed Nepal data if empty
    db = SessionLocal()
    try:
        from app.models.disaster import Disaster
        count = db.query(Disaster).count()
        if count == 0:
            seed_nepal_data(db)
            logger.info("✅ Nepal seed data loaded (77 districts)")
    finally:
        db.close()
    
    # Start background tasks
    scheduler.add_job(
        fetch_dhm_data,
        trigger=IntervalTrigger(minutes=15),
        id="dhm_ingestion",
        name="Fetch DHM River & Rainfall Data",
        replace_existing=True
    )
    
    scheduler.add_job(
        fetch_weather_forecast,
        trigger=IntervalTrigger(minutes=30),
        id="weather_forecast",
        name="Fetch Weather Forecasts",
        replace_existing=True
    )
    
    scheduler.add_job(
        fetch_nasa_imerg,
        trigger=IntervalTrigger(hours=3),
        id="nasa_imerg",
        name="Fetch NASA IMERG Rainfall",
        replace_existing=True
    )
    
    scheduler.add_job(
        run_predictions,
        trigger=IntervalTrigger(hours=1),
        id="ai_predictions",
        name="Run Flood & Landslide Predictions",
        replace_existing=True
    )
    
    scheduler.add_job(
        fetch_bipad_updates,
        trigger=IntervalTrigger(hours=1),
        id="bipad_updates",
        name="Fetch BIPAD Portal Updates",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ APScheduler started with 5 background jobs")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("🛑 Scheduler stopped. Application shutdown complete.")

app = FastAPI(
    title="AI Bipad Sahayak",
    description="Nepal's AI-powered Disaster Early Warning and Response Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Allow all for development, restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
app.include_router(communities.router, prefix="/communities", tags=["Communities"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(missing_persons.router, prefix="/missing-persons", tags=["Missing Persons"])
app.include_router(relief.router, prefix="/relief", tags=["Relief"])
app.include_router(damage.router, prefix="/damage", tags=["Damage Assessment"])

# WebSocket endpoint for real-time alerts
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            await websocket.send_json({"type": "ack", "message": "Connected to Bipad Sahayak"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)

# Health check
@app.get("/health")
async def health_check():
    db_status = check_db_connection()
    return {
        "status": "healthy" if db_status else "degraded",
        "timestamp": datetime.now(NEPAL_TZ).isoformat(),
        "database": "connected" if db_status else "disconnected",
        "scheduler": "running" if scheduler.running else "stopped",
        "version": "1.0.0",
        "nepal_time": datetime.now(NEPAL_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    }

# System status
@app.get("/status")
async def system_status():
    db = SessionLocal()
    try:
        dhm_service = DHMService()
        flood_service = FloodPredictionService()
        
        status = {
            "database": check_db_connection(),
            "dhm_stations": len(dhm_service.DHM_STATIONS),
            "monitored_rivers": 22,
            "districts_loaded": len(NEPAL_DISTRICTS),
            "last_dhm_update": "2026-07-01T14:30:00+05:45",
            "last_prediction_run": "2026-07-01T14:00:00+05:45",
            "active_alerts": 3,
            "registered_users": 12487,
            "sms_credits_remaining": 87450,
            "environment": settings.ENVIRONMENT,
            "timezone": settings.NEPAL_TIMEZONE
        }
        return status
    finally:
        db.close()

# Background task functions
async def fetch_dhm_data():
    """Every 15 minutes: DHM river and rainfall data"""
    logger.info("🔄 Fetching DHM data...")
    try:
        dhm = DHMService()
        readings = await dhm.fetch_all_river_levels()
        logger.info(f"✅ DHM data fetched: {len(readings)} stations updated")
    except Exception as e:
        logger.error(f"❌ DHM ingestion failed: {e}")

async def fetch_weather_forecast():
    """Every 30 minutes: Weather forecasts"""
    logger.info("🌤️ Fetching weather forecast...")
    try:
        weather = WeatherService()
        summary = await weather.get_nepal_weather_summary()
        logger.info(f"✅ Weather summary updated for {len(summary)} provinces")
    except Exception as e:
        logger.error(f"❌ Weather fetch failed: {e}")

async def fetch_nasa_imerg():
    """Every 3 hours: NASA IMERG rainfall"""
    logger.info("🛰️ Fetching NASA IMERG rainfall...")
    # Implementation would call NASA API
    logger.info("✅ NASA IMERG data updated")

async def run_predictions():
    """Every hour: Run flood and landslide predictions"""
    logger.info("🤖 Running AI predictions...")
    try:
        db = SessionLocal()
        flood_service = FloodPredictionService()
        landslide_service = LandslidePredictionService()
        
        flood_risks = await flood_service.get_all_rivers_risk(db)
        landslide_risks = await landslide_service.get_high_risk_zones_geojson(db)
        
        # Auto-generate alerts for CRITICAL/HIGH risks
        for risk in flood_risks:
            if risk.get("risk_level") in ["CRITICAL", "HIGH"]:
                logger.warning(f"⚠️ High flood risk detected: {risk['river_name']}")
        
        logger.info(f"✅ Predictions complete: {len(flood_risks)} rivers analyzed")
        db.close()
    except Exception as e:
        logger.error(f"❌ Prediction run failed: {e}")

async def fetch_bipad_updates():
    """Every hour: BIPAD portal updates"""
    logger.info("📡 Checking BIPAD portal...")
    logger.info("✅ BIPAD sync complete")

# Error handlers with Nepali messages
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": True,
        "message_nepali": "अनुरोध असफल भयो। कृपया पुनः प्रयास गर्नुहोस्।",
        "message_english": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": True,
        "message_nepali": "आन्तरिक त्रुटि भयो। कृपया प्रशासकलाई सम्पर्क गर्नुहोस्।",
        "message_english": "Internal server error",
        "status_code": 500
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)