from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.flood_prediction import FloodPredictionService
from app.services.landslide_prediction import LandslidePredictionService

router = APIRouter()
flood_service = FloodPredictionService()
landslide_service = LandslidePredictionService()

@router.get("/flood")
async def get_all_flood_risks(db: Session = Depends(get_db)):
    risks = await flood_service.get_all_rivers_risk(db)
    return risks

@router.get("/flood/{river_name}")
async def get_flood_risk(river_name: str, db: Session = Depends(get_db)):
    return await flood_service.predict_flood_risk(river_name, 24, db)

@router.get("/landslide")
async def get_landslide_map(db: Session = Depends(get_db)):
    return await landslide_service.get_high_risk_zones_geojson(db)

@router.get("/landslide/district/{district}")
async def get_district_landslide(district: str, db: Session = Depends(get_db)):
    return await landslide_service.calculate_district_landslide_risk(district, db)

@router.get("/summary")
async def prediction_summary(db: Session = Depends(get_db)):
    flood_risks = await flood_service.get_all_rivers_risk(db)
    critical = [r for r in flood_risks if r.get("risk_level") in ["CRITICAL", "HIGH"]]
    return {
        "critical_flood_rivers": len(critical),
        "total_rivers_monitored": len(flood_risks),
        "highest_risk": critical[0] if critical else None,
        "last_updated": "2026-07-01T14:45:00+05:45"
    }