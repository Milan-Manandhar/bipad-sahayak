from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class ReliefCategory(str, enum.Enum):
    FOOD = "food"
    WATER = "water"
    SHELTER = "shelter"
    MEDICAL = "medical"
    CLOTHING = "clothing"
    RESCUE_EQUIPMENT = "rescue_equipment"
    OTHER = "other"

class ReliefInventory(Base):
    __tablename__ = "relief_inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_category = Column(Enum(ReliefCategory), nullable=False, index=True)
    item_name_nepali = Column(String(255), nullable=False)
    item_name_english = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    location_description = Column(String(500), nullable=True)
    district = Column(String(100), nullable=False, index=True)
    vdc = Column(String(150), nullable=True)
    
    organization_name = Column(String(255), nullable=False)
    contact_person = Column(String(150), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    
    vehicle_available = Column(Boolean, default=False)
    vehicle_type = Column(String(100), nullable=True)
    
    available_from = Column(DateTime(timezone=True), server_default=func.now())
    available_until = Column(DateTime(timezone=True), nullable=True)
    is_available = Column(Boolean, default=True, index=True)
    
    assigned_to_disaster_id = Column(UUID(as_uuid=True), ForeignKey("disasters.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())