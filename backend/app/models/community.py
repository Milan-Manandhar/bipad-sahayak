from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class RoadAccess(str, enum.Enum):
    MOTORABLE_YEAR_ROUND = "motorable_year_round"
    SEASONAL = "seasonal"
    FOOTPATH_ONLY = "footpath_only"

class Community(Base):
    __tablename__ = "communities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_nepali = Column(String(255), nullable=False)
    name_english = Column(String(255), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    province = Column(String(100), nullable=False)
    vdc_municipality = Column(String(150), nullable=False)
    ward_number = Column(Integer, nullable=False)
    tole_name = Column(String(150), nullable=True)
    
    population = Column(Integer, nullable=False)
    household_count = Column(Integer, nullable=False)
    vulnerable_count = Column(Integer, nullable=True)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_masl = Column(Float, nullable=True)
    
    flood_risk_score = Column(Float, default=0.0)
    landslide_risk_score = Column(Float, default=0.0)
    earthquake_vulnerability = Column(Float, default=0.0)
    
    primary_evacuation_point_name = Column(String(255), nullable=True)
    primary_evacuation_point_lat = Column(Float, nullable=True)
    primary_evacuation_point_lon = Column(Float, nullable=True)
    primary_evacuation_capacity = Column(Integer, nullable=True)
    
    secondary_evacuation_point_name = Column(String(255), nullable=True)
    secondary_evacuation_lat = Column(Float, nullable=True)
    secondary_evacuation_lon = Column(Float, nullable=True)
    
    evacuation_route_geojson = Column(JSON, nullable=True)
    
    local_authority_name = Column(String(255), nullable=True)
    local_authority_phone = Column(String(20), nullable=True)
    
    volunteer_count = Column(Integer, default=0)
    volunteer_contact_phone = Column(String(20), nullable=True)
    
    nearest_hospital_name = Column(String(255), nullable=True)
    nearest_hospital_km = Column(Float, nullable=True)
    
    road_access = Column(Enum(RoadAccess), default=RoadAccess.MOTORABLE_YEAR_ROUND)
    mobile_coverage = Column(Boolean, default=True)
    registered_phone_numbers = Column(JSON, nullable=True)
    
    last_disaster_type = Column(String(50), nullable=True)
    last_disaster_date = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_community_district_risk', 'district', 'flood_risk_score'),
    )