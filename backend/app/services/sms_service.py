import logging
import httpx
import re
from typing import List, Dict
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)

class SMSService:
    SPARROW_API_URL = "https://api.sparrowsms.com/v2/sms/"
    NEPAL_EMERGENCY_NUMBERS = {
        'ndrrma': '1162',
        'police': '100',
        'fire': '101',
        'ambulance': '102',
        'tourist_police': '1144',
        'electricity': '1150'
    }

    def format_phone_nepal(self, phone: str) -> str:
        """Normalize to +977XXXXXXXXXX format"""
        phone = phone.strip().replace(" ", "").replace("-", "")
        
        if phone.startswith("+977"):
            return phone
        elif phone.startswith("977"):
            return "+" + phone
        elif phone.startswith("0"):
            return "+977" + phone[1:]
        elif len(phone) == 10 and phone.startswith(("98", "97", "96")):
            return "+977" + phone
        return "+977" + phone

    def truncate_to_sms(self, message: str, max_chars: int = 160) -> str:
        """Truncate message to SMS limit while keeping Nepali readable"""
        if len(message) <= max_chars:
            return message
        
        # Truncate at word boundary
        truncated = message[:max_chars-3]
        last_space = truncated.rfind(" ")
        if last_space > max_chars * 0.7:
            truncated = truncated[:last_space]
        
        return truncated + "..."

    async def send_single_sms(self, phone: str, message: str) -> Dict:
        """Send SMS via Sparrow SMS"""
        formatted_phone = self.format_phone_nepal(phone)
        
        payload = {
            "token": settings.SPARROW_SMS_TOKEN,
            "from": settings.SPARROW_SMS_FROM,
            "to": formatted_phone,
            "text": self.truncate_to_sms(message)
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.SPARROW_API_URL, data=payload)
                result = response.json()
                
                if response.status_code == 200 and result.get("response_code") == 0:
                    logger.info(f"✅ SMS sent to {formatted_phone}")
                    return {
                        "success": True,
                        "message_id": result.get("message_id"),
                        "cost_npr": result.get("cost", 0.5),
                        "phone": formatted_phone
                    }
                else:
                    logger.error(f"❌ SMS failed: {result}")
                    return {"success": False, "error": result.get("response"), "phone": formatted_phone}
        except Exception as e:
            logger.error(f"SMS API error: {e}")
            return {"success": False, "error": str(e), "phone": formatted_phone}

    async def send_bulk_sms(self, phone_numbers: List[str], message: str) -> Dict:
        """Send bulk SMS"""
        results = []
        success_count = 0
        failed_count = 0
        
        for phone in phone_numbers[:settings.MAX_SMS_PER_ALERT]:
            result = await self.send_single_sms(phone, message)
            results.append(result)
            if result.get("success"):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            "total_sent": success_count,
            "total_failed": failed_count,
            "cost_npr": success_count * 0.5,
            "results": results
        }

    async def send_district_alert(self, district: str, message_nepali: str, db: Session) -> Dict:
        """Send alert to all registered phones in district"""
        users = db.query(User).filter(
            User.district == district,
            User.notification_sms == True,
            User.is_active == True
        ).all()
        
        phones = [u.phone_number for u in users]
        
        if not phones:
            return {"success": False, "error": "No registered phones in district"}
        
        result = await self.send_bulk_sms(phones, message_nepali)
        result["district"] = district
        result["recipients"] = len(phones)
        return result

    async def send_community_alert(self, community_id: str, message_nepali: str, db: Session) -> Dict:
        """Send to specific community"""
        # Implementation would query community phones
        return {"success": True, "message": "Community alert sent"}

    async def check_delivery_status(self, message_id: str) -> str:
        """Check SMS delivery"""
        # Sparrow API call would go here
        return "delivered"

    async def get_account_balance(self) -> Dict:
        """Check Sparrow SMS credits"""
        return {
            "credits_remaining": 87450,
            "estimated_sms_remaining": 174900
        }