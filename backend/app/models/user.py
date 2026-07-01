from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    VOLUNTEER = "volunteer"
    WARD_AUTHORITY = "ward_authority"
    VDC_AUTHORITY = "vdc_authority"
    CDO = "cdo"
    DDMC = "ddmc"
    PROVINCE_AUTHORITY = "province_authority"
    NDRRMA = "ndrrma"
    NGO_WORKER = "ngo_worker"
    JOURNALIST = "journalist"
    ADMIN = "admin"

class LanguagePreference(str, enum.Enum):
    NEPALI = "nepali"
    ENGLISH = "english"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, index=True)
    district = Column(String(100), nullable=True, index=True)
    vdc = Column(String(150), nullable=True)
    ward = Column(Integer, nullable=True)
    organization_name = Column(String(255), nullable=True)
    
    language_preference = Column(Enum(LanguagePreference), default=LanguagePreference.NEPALI)
    
    notification_sms = Column(Boolean, default=True)
    notification_push = Column(Boolean, default=True)
    notification_whatsapp = Column(Boolean, default=False)
    
    community_id = Column(UUID(as_uuid=True), ForeignKey("communities.id"), nullable=True)
    firebase_token = Column(String(500), nullable=True)
    
    otp_code = Column(String(10), nullable=True)
    otp_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_user_district_role', 'district', 'role'),
    )