from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum, BigInteger, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import uuid
import enum
from app.database import Base

class DisasterType(str, enum.Enum):
    FLOOD = "flood"
    LANDSLIDE = "landslide"
    EARTHQUAKE = "earthquake"
    FIRE = "fire"
    COLD_WAVE = "cold_wave"
    DROUGHT = "drought"
    STORM = "storm"

class ResponseStatus(str, enum.Enum):
    MONITORING = "monitoring"
    ACTIVE = "active"
    CONTAINED = "contained"
    CLOSED = "closed"

class Disaster(Base):
    __tablename__ = "disasters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(DisasterType), nullable=False, index=True)
    severity = Column(Integer, nullable=False)  # 1-5
    title_nepali = Column(String(255), nullable=False)
    title_english = Column(String(255), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    vdc_municipality = Column(String(150), nullable=True)
    ward_number = Column(Integer, nullable=True)
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    affected_area_geojson = Column(JSON, nullable=True)
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    predicted_impact_population = Column(Integer, nullable=True)
    predicted_impact_households = Column(Integer, nullable=True)
    actual_deaths = Column(Integer, nullable=True)
    actual_injured = Column(Integer, nullable=True)
    actual_displaced = Column(Integer, nullable=True)
    actual_economic_loss_npr = Column(BigInteger, nullable=True)
    prediction_confidence_score = Column(Float, nullable=True)
    data_sources_used = Column(JSON, nullable=True)
    response_status = Column(Enum(ResponseStatus), default=ResponseStatus.MONITORING, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_disaster_district_type', 'district', 'type'),
        Index('idx_disaster_severity_created', 'severity', 'created_at'),
    )