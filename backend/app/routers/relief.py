from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.relief import ReliefInventory

router = APIRouter()

@router.get("/available")
async def available_relief(district: str = None, db: Session = Depends(get_db)):
    query = db.query(ReliefInventory).filter(ReliefInventory.is_available == True)
    if district:
        query = query.filter(ReliefInventory.district == district)
    return query.limit(50).all()

@router.post("/")
async def register_relief(data: dict, db: Session = Depends(get_db)):
    item = ReliefInventory(**data)
    db.add(item)
    db.commit()
    return {"success": True, "id": str(item.id)}