from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.sensor import RiverSensor, RainfallSensor

router = APIRouter()

@router.get("/rivers")
async def get_river_sensors(db: Session = Depends(get_db)):
    sensors = db.query(RiverSensor).filter(RiverSensor.is_active == True).all()
    return [
        {
            "id": str(s.id),
            "river_name": s.river_name,
            "station_name": s.station_name,
            "district": s.district,
            "current_level_m": s.current_level_m,
            "danger_level_m": s.danger_level_m,
            "status": s.status.value,
            "last_reading_at": s.last_reading_at.isoformat() if s.last_reading_at else None
        } for s in sensors
    ]

@router.get("/rivers/{river_name}")
async def get_river_status(river_name: str, db: Session = Depends(get_db)):
    sensor = db.query(RiverSensor).filter(RiverSensor.river_name == river_name).first()
    if not sensor:
        return {"error": "River not found"}
    return sensor

@router.get("/rainfall")
async def get_rainfall_sensors(db: Session = Depends(get_db)):
    sensors = db.query(RainfallSensor).all()
    return sensors

@router.get("/danger")
async def get_danger_stations(db: Session = Depends(get_db)):
    rivers = db.query(RiverSensor).filter(RiverSensor.status.in_(["warning", "danger", "extreme"])).all()
    rainfall = db.query(RainfallSensor).filter(RainfallSensor.current_status.in_(["warning", "danger"])).all()
    return {"rivers": rivers, "rainfall": rainfall}