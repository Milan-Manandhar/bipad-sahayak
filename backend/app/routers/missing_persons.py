from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.missing_person import MissingPerson, MissingStatus

router = APIRouter()

class MissingPersonCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    last_seen_location_description: str
    contact_person_name: str
    contact_person_phone: str
    physical_description: Optional[str] = None

@router.post("/")
async def report_missing_person(request: MissingPersonCreate, db: Session = Depends(get_db)):
    person = MissingPerson(**request.dict())
    db.add(person)
    db.commit()
    db.refresh(person)
    return {"success": True, "id": str(person.id)}

@router.get("/active")
async def get_active_missing(db: Session = Depends(get_db)):
    persons = db.query(MissingPerson).filter(MissingPerson.status == MissingStatus.MISSING).all()
    return persons

@router.put("/{person_id}/found")
async def mark_found(person_id: str, found_location: str, db: Session = Depends(get_db)):
    person = db.query(MissingPerson).filter(MissingPerson.id == person_id).first()
    if not person:
        raise HTTPException(404, "Person not found")
    person.status = MissingStatus.FOUND_SAFE
    person.found_location = found_location
    db.commit()
    return {"success": True}