from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
import random
import string

from app.database import get_db
from app.models.user import User, UserRole, LanguagePreference
from app.config import settings
from app.services.sms_service import SMSService

router = APIRouter()
security = HTTPBearer()
sms_service = SMSService()

class OTPRequest(BaseModel):
    phone_number: str

class OTPVerify(BaseModel):
    phone_number: str
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/request-otp")
async def request_otp(request: OTPRequest, db: Session = Depends(get_db)):
    """Request OTP via Sparrow SMS"""
    phone = sms_service.format_phone_nepal(request.phone_number)
    
    # Generate 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    # Save OTP to user (create if not exists)
    user = db.query(User).filter(User.phone_number == phone).first()
    if not user:
        user = User(
            phone_number=phone,
            name="नयाँ प्रयोगकर्ता",
            role=UserRole.CITIZEN,
            otp_code=otp,
            otp_expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.add(user)
    else:
        user.otp_code = otp
        user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    db.commit()
    
    # Send SMS
    message = f"AI बिपद सहायक OTP: {otp}\nयो OTP १० मिनेटका लागि मान्य छ।"
    await sms_service.send_single_sms(phone, message)
    
    return {"success": True, "message": "OTP पठाइयो", "phone": phone}

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and return JWT"""
    phone = sms_service.format_phone_nepal(request.phone_number)
    user = db.query(User).filter(User.phone_number == phone).first()
    
    if not user or user.otp_code != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    
    # Clear OTP
    user.otp_code = None
    user.otp_expires_at = None
    user.is_verified = True
    db.commit()
    
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    
    return TokenResponse(
        access_token=token,
        user={
            "id": str(user.id),
            "phone": user.phone_number,
            "name": user.name,
            "role": user.role.value,
            "district": user.district,
            "language": user.language_preference.value
        }
    )

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "phone": current_user.phone_number,
        "name": current_user.name,
        "role": current_user.role.value,
        "district": current_user.district,
        "language": current_user.language_preference.value
    }

@router.post("/register-firebase-token")
async def register_firebase(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.firebase_token = token
    db.commit()
    return {"success": True}