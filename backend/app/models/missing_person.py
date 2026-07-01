from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class MissingStatus(str, enum.Enum):
    MISSING = "missing"
    FOUND_SAFE = "found_safe"
    FOUND_DECEASED = "found_deceased"
    SEARCHING = "searching"

class MissingPerson(Base):
    __tablename__ = "missing_persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    disaster_id = Column(UUID(as_uuid=True), ForeignKey("disasters.id"), nullable=True)
    
    name = Column(String(150), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    
    photo_url = Column(String(500), nullable=True)
    additional_photos = Column(JSON, nullable=True)
    
    last_seen_lat = Column(Float, nullable=True)
    last_seen_lon = Column(Float, nullable=True)
    last_seen_location_description = Column(String(500), nullable=True)
    last_seen_datetime = Column(DateTime(timezone=True), nullable=True)
    
    physical_description = Column(Text, nullable=True)
    clothing_description = Column(String(500), nullable=True)
    distinctive_features = Column(String(500), nullable=True)
    
    contact_person_name = Column(String(150), nullable=False)
    contact_person_phone = Column(String(20), nullable=False)
    relationship = Column(String(100), nullable=True)
    
    status = Column(Enum(MissingStatus), default=MissingStatus.MISSING, index=True)
    found_location = Column(String(500), nullable=True)
    found_datetime = Column(DateTime(timezone=True), nullable=True)
    
    face_encoding = Column(JSON, nullable=True)
    
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)