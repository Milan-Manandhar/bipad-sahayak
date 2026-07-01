from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class RiverStatus(str, enum.Enum):
    NORMAL = "normal"
    WATCH = "watch"
    WARNING = "warning"
    DANGER = "danger"
    EXTREME = "extreme"

class RainfallStatus(str, enum.Enum):
    NORMAL = "normal"
    WATCH = "watch"
    WARNING = "warning"
    DANGER = "danger"

class RiverSensor(Base):
    __tablename__ = "river_sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dhm_station_id = Column(String(20), unique=True, nullable=False, index=True)
    river_name = Column(String(100), nullable=False, index=True)
    station_name = Column(String(150), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    vdc = Column(String(150), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_masl = Column(Float, nullable=True)
    
    current_level_m = Column(Float, nullable=True)
    normal_level_m = Column(Float, nullable=True)
    warning_level_m = Column(Float, nullable=True)
    danger_level_m = Column(Float, nullable=True)
    extreme_danger_level_m = Column(Float, nullable=True)
    
    current_flow_cumecs = Column(Float, nullable=True)
    level_change_3h = Column(Float, nullable=True)
    level_change_24h = Column(Float, nullable=True)
    
    status = Column(Enum(RiverStatus), default=RiverStatus.NORMAL, index=True)
    battery_level = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    last_reading_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_river_status_district', 'status', 'district'),
    )

class RainfallSensor(Base):
    __tablename__ = "rainfall_sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dhm_station_id = Column(String(20), unique=True, nullable=False, index=True)
    station_name = Column(String(150), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    vdc = Column(String(150), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=True)
    
    rainfall_1h_mm = Column(Float, default=0.0)
    rainfall_3h_mm = Column(Float, default=0.0)
    rainfall_6h_mm = Column(Float, default=0.0)
    rainfall_12h_mm = Column(Float, default=0.0)
    rainfall_24h_mm = Column(Float, default=0.0)
    rainfall_72h_mm = Column(Float, default=0.0)
    
    warning_threshold_mm = Column(Float, default=80.0)
    danger_threshold_mm = Column(Float, default=150.0)
    
    current_status = Column(Enum(RainfallStatus), default=RainfallStatus.NORMAL, index=True)
    last_reading_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())