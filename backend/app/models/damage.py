from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum, Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class StructureType(str, enum.Enum):
    HOUSE = "house"
    SCHOOL = "school"
    HOSPITAL = "hospital"
    ROAD = "road"
    BRIDGE = "bridge"
    AGRICULTURAL_LAND = "agricultural_land"
    GOVERNMENT_BUILDING = "government_building"
    TEMPLE = "temple"
    OTHER = "other"

class DamageLevel(str, enum.Enum):
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    DESTROYED = "destroyed"

class DamageAssessment(Base):
    __tablename__ = "damage_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    disaster_id = Column(UUID(as_uuid=True), ForeignKey("disasters.id"), nullable=False)
    assessor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    assessment_datetime = Column(DateTime(timezone=True), server_default=func.now())
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    district = Column(String(100), nullable=False, index=True)
    vdc = Column(String(150), nullable=True)
    ward = Column(Integer, nullable=True)
    
    structure_type = Column(Enum(StructureType), nullable=False)
    damage_level = Column(Enum(DamageLevel), nullable=False)
    affected_people_count = Column(Integer, nullable=True)
    estimated_cost_npr = Column(BigInteger, nullable=True)
    
    photos = Column(JSON, nullable=True)
    needs_immediate_attention = Column(Boolean, default=False)
    priority_level = Column(Integer, default=3)
    notes_nepali = Column(Text, nullable=True)
    
    is_verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())