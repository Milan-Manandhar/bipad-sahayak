from sqlalchemy.orm import Session
from app.models.community import Community
from app.models.sensor import RiverSensor, RainfallSensor, RiverStatus, RainfallStatus
from app.models.user import User, UserRole
from app.utils.nepal_districts import NEPAL_DISTRICTS
from datetime import datetime
import pytz

NEPAL_TZ = pytz.timezone("Asia/Kathmandu")

def seed_nepal_data(db: Session):
    print("🌱 Seeding Nepal data...")
    
    # Seed 77 districts (we use the provided list)
    print(f"  → Seeding {len(NEPAL_DISTRICTS)} districts (partial for demo)")
    
    # Seed sample communities
    communities_data = [
        {
            "name_nepali": "चौतारा नगरपालिका", "name_english": "Chautara Municipality",
            "district": "Sindhupalchowk", "province": "बागमती प्रदेश",
            "vdc_municipality": "Chautara", "ward_number": 5,
            "population": 12450, "household_count": 2450,
            "latitude": 27.98, "longitude": 85.69,
            "flood_risk_score": 82.0, "landslide_risk_score": 91.0,
            "primary_evacuation_point_name": "Chautara Higher Secondary School",
            "primary_evacuation_point_lat": 27.982, "primary_evacuation_point_lon": 85.692,
            "primary_evacuation_capacity": 2500,
            "local_authority_phone": "+977-11-692345",
            "registered_phone_numbers": ["+9779800001122", "+9779800003344"]
        },
        {
            "name_nepali": "भरतपुर महानगरपालिका", "name_english": "Bharatpur Metropolitan",
            "district": "Chitwan", "province": "बागमती प्रदेश",
            "vdc_municipality": "Bharatpur", "ward_number": 12,
            "population": 28500, "household_count": 5820,
            "latitude": 27.68, "longitude": 84.43,
            "flood_risk_score": 68.0, "landslide_risk_score": 35.0,
            "primary_evacuation_point_name": "Bharatpur Stadium",
            "primary_evacuation_point_lat": 27.685, "primary_evacuation_point_lon": 84.435,
            "primary_evacuation_capacity": 8000,
            "local_authority_phone": "+977-56-570123"
        }
    ]
    
    for c_data in communities_data:
        community = Community(**c_data)
        db.add(community)
    
    # Seed River Sensors
    river_sensors = [
        {"dhm_station_id": "BG001", "river_name": "Bagmati", "station_name": "Chobar", "district": "Kathmandu", "latitude": 27.6742, "longitude": 85.2817, "current_level_m": 2.34, "danger_level_m": 3.5, "status": RiverStatus.WATCH, "last_reading_at": datetime.now(NEPAL_TZ)},
        {"dhm_station_id": "KS001", "river_name": "Koshi", "station_name": "Chatara", "district": "Sunsari", "latitude": 26.8518, "longitude": 87.1578, "current_level_m": 6.82, "danger_level_m": 9.0, "status": RiverStatus.WARNING, "last_reading_at": datetime.now(NEPAL_TZ)},
        {"dhm_station_id": "KR001", "river_name": "Karnali", "station_name": "Chisapani", "district": "Bardiya", "latitude": 28.6318, "longitude": 81.2833, "current_level_m": 5.9, "danger_level_m": 13.0, "status": RiverStatus.NORMAL, "last_reading_at": datetime.now(NEPAL_TZ)},
        {"dhm_station_id": "NR001", "river_name": "Narayani", "station_name": "Narayanghat", "district": "Chitwan", "latitude": 27.6883, "longitude": 84.4258, "current_level_m": 4.1, "danger_level_m": 8.5, "status": RiverStatus.NORMAL, "last_reading_at": datetime.now(NEPAL_TZ)},
    ]
    
    for rs in river_sensors:
        sensor = RiverSensor(**rs)
        db.add(sensor)
    
    # Seed Rainfall Sensors
    rainfall_sensors = [
        {"dhm_station_id": "RF_KTM01", "station_name": "Kathmandu Airport", "district": "Kathmandu", "latitude": 27.6964, "longitude": 85.3591, "rainfall_24h_mm": 42.3, "current_status": RainfallStatus.NORMAL},
        {"dhm_station_id": "RF_SPK01", "station_name": "Chautara", "district": "Sindhupalchowk", "latitude": 27.98, "longitude": 85.69, "rainfall_24h_mm": 187.4, "current_status": RainfallStatus.DANGER},
    ]
    
    for rfs in rainfall_sensors:
        sensor = RainfallSensor(**rfs)
        db.add(sensor)
    
    # Seed sample admin user
    admin_user = User(
        phone_number="+9779800000001",
        name="प्रशासक",
        role=UserRole.ADMIN,
        district="Kathmandu",
        is_verified=True,
        notification_sms=True
    )
    db.add(admin_user)
    
    db.commit()
    print("✅ Nepal seed data loaded successfully!")