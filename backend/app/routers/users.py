from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return user

@router.put("/profile")
async def update_profile(data: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    return {"success": True}