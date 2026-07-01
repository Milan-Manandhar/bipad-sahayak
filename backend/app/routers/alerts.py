from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.database import get_db
from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.alert_distribution import AlertDistributionService

router = APIRouter()
distributor = AlertDistributionService()

class CreateAlertRequest(BaseModel):
    type: AlertType
    severity: AlertSeverity
    title_nepali: str
    title_english: str
    message_nepali: str
    message_english: str
    sms_message_nepali: str
    affected_districts: List[str]
    affected_vdcs: Optional[List[str]] = None
    estimated_affected_population: Optional[int] = None
    safe_zones: Optional[list] = None
    channels_used: List[str] = ["sms", "push"]

@router.get("/")
async def list_alerts(
    district: Optional[str] = None,
    severity: Optional[AlertSeverity] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if active_only:
        query = query.filter(Alert.is_active == True)
    if district:
        query = query.filter(Alert.affected_districts.contains([district]))
    if severity:
        query = query.filter(Alert.severity == severity)
    
    alerts = query.order_by(Alert.issued_at.desc()).limit(50).all()
    return [
        {
            "id": str(a.id),
            "alert_code": a.alert_code,
            "title_nepali": a.title_nepali,
            "severity": a.severity.value,
            "type": a.type.value,
            "affected_districts": a.affected_districts,
            "issued_at": a.issued_at.isoformat(),
            "sms_sent_count": a.sms_sent_count
        } for a in alerts
    ]

@router.post("/")
async def create_alert(
    request: CreateAlertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["ndrrma", "cdo", "ddmc", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    alert_code = f"BIPAD-2083-{request.type.value.upper()}-{str(uuid.uuid4())[:8].upper()}"
    
    alert = Alert(
        alert_code=alert_code,
        type=request.type,
        severity=request.severity,
        title_nepali=request.title_nepali,
        title_english=request.title_english,
        message_nepali=request.message_nepali,
        message_english=request.message_english,
        sms_message_nepali=request.sms_message_nepali,
        affected_districts=request.affected_districts,
        affected_vdcs=request.affected_vdcs,
        estimated_affected_population=request.estimated_affected_population,
        safe_zones=request.safe_zones,
        channels_used=request.channels_used,
        issued_by=current_user.id
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # Distribute immediately
    await distributor.distribute_alert(str(alert.id), db)
    
    return {"success": True, "alert_id": str(alert.id), "alert_code": alert_code}

@router.get("/{alert_id}")
async def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.put("/{alert_id}/cancel")
async def cancel_alert(
    alert_id: str,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = await distributor.send_cancellation(alert_id, reason, db)
    return result

@router.get("/district/{district_name}")
async def alerts_by_district(district_name: str, db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(
        Alert.affected_districts.contains([district_name]),
        Alert.is_active == True
    ).all()
    return alerts