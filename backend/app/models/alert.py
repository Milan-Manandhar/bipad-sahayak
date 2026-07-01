from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class AlertSeverity(str, enum.Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"
    EMERGENCY = "emergency"

class AlertType(str, enum.Enum):
    FLOOD = "flood"
    LANDSLIDE = "landslide"
    EARTHQUAKE = "earthquake"
    FIRE = "fire"
    STORM = "storm"
    COLD_WAVE = "cold_wave"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_code = Column(String(50), unique=True, nullable=False, index=True)  # BIPAD-2081-FLOOD-001
    disaster_id = Column(UUID(as_uuid=True), ForeignKey("disasters.id"), nullable=True)
    type = Column(Enum(AlertType), nullable=False, index=True)
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    
    title_nepali = Column(String(255), nullable=False)
    title_english = Column(String(255), nullable=False)
    message_nepali = Column(Text, nullable=False)
    message_english = Column(Text, nullable=False)
    sms_message_nepali = Column(String(160), nullable=False)
    
    affected_districts = Column(JSON, nullable=False)
    affected_vdcs = Column(JSON, nullable=True)
    affected_wards = Column(JSON, nullable=True)
    
    estimated_affected_population = Column(Integer, nullable=True)
    safe_zones = Column(JSON, nullable=True)
    evacuation_routes = Column(JSON, nullable=True)
    do_this_now_steps_nepali = Column(JSON, nullable=True)
    emergency_contacts = Column(JSON, nullable=True)
    
    channels_used = Column(JSON, nullable=True)
    sms_sent_count = Column(Integer, default=0)
    sms_delivered_count = Column(Integer, default=0)
    push_sent_count = Column(Integer, default=0)
    whatsapp_sent_count = Column(Integer, default=0)
    
    issued_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    prediction_confidence = Column(Float, nullable=True)
    
    is_active = Column(Boolean, default=True, index=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancel_reason = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_alert_active_severity', 'is_active', 'severity'),
        Index('idx_alert_district_type', 'type', 'issued_at'),
    )