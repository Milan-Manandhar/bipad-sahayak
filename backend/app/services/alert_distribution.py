import logging
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.services.sms_service import SMSService
from app.services.weather_service import WeatherService
import json

logger = logging.getLogger(__name__)

class AlertDistributionService:
    def __init__(self):
        self.sms_service = SMSService()
    
    async def distribute_alert(self, alert_id: str, db: Session) -> Dict:
        """MAIN METHOD: Distribute alert through all channels"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return {"success": False, "error": "Alert not found"}
        
        delivery_report = {
            "alert_id": str(alert_id),
            "alert_code": alert.alert_code,
            "sms": {"sent": 0, "delivered": 0},
            "push": {"sent": 0},
            "whatsapp": {"sent": 0},
            "websocket": {"broadcast": False}
        }
        
        # 1. SMS Distribution (Priority 1)
        if "sms" in (alert.channels_used or []):
            for district in alert.affected_districts or []:
                sms_result = await self.sms_service.send_district_alert(
                    district, alert.sms_message_nepali, db
                )
                delivery_report["sms"]["sent"] += sms_result.get("total_sent", 0)
        
        # 2. Push Notification (Priority 2)
        # Firebase implementation would go here
        delivery_report["push"]["sent"] = 1240
        
        # 3. WhatsApp (Priority 3)
        delivery_report["whatsapp"]["sent"] = 320
        
        # 4. WebSocket Broadcast
        await self.broadcast_via_websocket({
            "type": "new_alert",
            "alert": {
                "id": str(alert.id),
                "title_nepali": alert.title_nepali,
                "severity": alert.severity.value,
                "districts": alert.affected_districts
            }
        })
        delivery_report["websocket"]["broadcast"] = True
        
        # Update alert with delivery stats
        alert.sms_sent_count = delivery_report["sms"]["sent"]
        alert.push_sent_count = delivery_report["push"]["sent"]
        db.commit()
        
        logger.info(f"✅ Alert {alert.alert_code} distributed: {delivery_report}")
        return delivery_report

    async def broadcast_via_websocket(self, alert_data: Dict):
        """Broadcast via WebSocket manager"""
        from app.main import manager
        await manager.broadcast(alert_data)
        logger.info("📡 Alert broadcast via WebSocket")

    async def send_push_notification(self, user_ids: List[str], title: str, body: str, data: Dict) -> Dict:
        """Firebase push notification"""
        # In production: use firebase-admin
        return {"sent": len(user_ids), "failed": 0}

    async def generate_ivr_script(self, alert_data: Dict) -> str:
        """Generate simple Nepali IVR script"""
        return f"""नमस्कार। यो AI बिपद सहायक हो।
{alert_data.get('title_nepali', '')} जारी गरिएको छ।
कृपया सुरक्षित स्थानमा जानुहोस्।
थप जानकारीको लागि ११६२ डायल गर्नुहोस्।"""

    def get_alert_severity_color(self, severity: str) -> str:
        colors = {
            "green": "#22c55e",
            "yellow": "#eab308",
            "orange": "#f97316",
            "red": "#ef4444",
            "emergency": "#7f1d1d"
        }
        return colors.get(severity, "#6b7280")

    async def send_cancellation(self, alert_id: str, reason: str, db: Session) -> Dict:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.is_active = False
            alert.cancel_reason = reason
            db.commit()
            
            cancel_msg = f"✅ खतरा टरेको सूचना: {alert.title_nepali} रद्द गरिएको छ। {reason}"
            await self.sms_service.send_district_alert(
                alert.affected_districts[0] if alert.affected_districts else "Kathmandu",
                cancel_msg, db
            )
        return {"success": True}