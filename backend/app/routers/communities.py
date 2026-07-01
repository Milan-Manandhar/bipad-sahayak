from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.community import Community

router = APIRouter()

@router.get("/")
async def list_communities(district: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Community)
    if district:
        query = query.filter(Community.district == district)
    return query.limit(100).all()

@router.get("/high-risk")
async def high_risk_communities(db: Session = Depends(get_db)):
    communities = db.query(Community).order_by(
        (Community.flood_risk_score + Community.landslide_risk_score).desc()
    ).limit(50).all()
    return communities

@router.get("/{community_id}")
async def get_community(community_id: str, db: Session = Depends(get_db)):
    return db.query(Community).filter(Community.id == community_id).first()