import logging
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.sensor import RainfallSensor
from app.utils.nepal_districts import NEPAL_DISTRICTS
import pytz

logger = logging.getLogger(__name__)
NEPAL_TZ = pytz.timezone("Asia/Kathmandu")

class LandslidePredictionService:
    NEPAL_LANDSLIDE_CONFIG = {
        'high_risk_districts': [
            'Sindhupalchowk', 'Kaski', 'Myagdi', 'Baglung', 'Parbat',
            'Syangja', 'Lamjung', 'Gorkha', 'Dhading', 'Nuwakot',
            'Rasuwa', 'Dolakha', 'Ramechhap', 'Okhaldhunga', 'Solukhumbu',
            'Taplejung', 'Panchthar', 'Ilam', 'Bhojpur', 'Terhathum',
            'Sankhuwasabha', 'Khotang', 'Udayapur', 'Arghakhanchi'
        ],
        'geological_risk': {
            'schist': 1.8, 'phyllite': 1.6, 'slate': 1.5, 'shale': 1.4,
            'limestone': 1.2, 'sandstone': 1.1, 'quartzite': 0.8,
            'granite': 0.7, 'gneiss': 0.9
        },
        'rainfall_thresholds': {
            'low': {'24h': 50, '72h': 100},
            'medium': {'24h': 80, '72h': 150},
            'high': {'24h': 120, '72h': 220},
            'critical': {'24h': 180, '72h': 300}
        },
        'slope_risk': {
            'flat_0_15': 0.1, 'gentle_15_30': 0.4, 'moderate_30_45': 0.8,
            'steep_45_60': 1.5, 'very_steep_60plus': 2.0
        }
    }

    def calculate_antecedent_rainfall_index(self, rainfall_history: List[float]) -> float:
        """15-day weighted antecedent rainfall index"""
        if not rainfall_history:
            return 30.0
        
        weights = [0.5, 0.45, 0.4, 0.36, 0.32, 0.29, 0.26, 0.23, 0.21, 0.19, 
                   0.17, 0.15, 0.14, 0.12, 0.11]
        weighted = sum(r * w for r, w in zip(rainfall_history[:15], weights))
        return min(weighted, 250.0)

    def assess_slope_risk(self, slope_degrees: float) -> float:
        if slope_degrees < 15:
            return self.NEPAL_LANDSLIDE_CONFIG['slope_risk']['flat_0_15']
        elif slope_degrees < 30:
            return self.NEPAL_LANDSLIDE_CONFIG['slope_risk']['gentle_15_30']
        elif slope_degrees < 45:
            return self.NEPAL_LANDSLIDE_CONFIG['slope_risk']['moderate_30_45']
        elif slope_degrees < 60:
            return self.NEPAL_LANDSLIDE_CONFIG['slope_risk']['steep_45_60']
        else:
            return self.NEPAL_LANDSLIDE_CONFIG['slope_risk']['very_steep_60plus']

    async def calculate_district_landslide_risk(self, district: str, db: Session) -> Dict:
        """Calculate landslide risk for a district"""
        district_info = next((d for d in NEPAL_DISTRICTS if d['name_english'] == district), None)
        if not district_info:
            return {"error": "District not found"}

        # Get rainfall data
        rainfall_sensors = db.query(RainfallSensor).filter(
            RainfallSensor.district == district
        ).all() if db else []
        
        rainfall_24h = sum([s.rainfall_24h_mm or 0 for s in rainfall_sensors]) / max(len(rainfall_sensors), 1)
        rainfall_72h = sum([s.rainfall_72h_mm or 0 for s in rainfall_sensors]) / max(len(rainfall_sensors), 1)
        
        # Antecedent rainfall
        ari = self.calculate_antecedent_rainfall_index([rainfall_24h] * 15)
        
        # Base risk
        base_risk = 0.3
        if district in self.NEPAL_LANDSLIDE_CONFIG['high_risk_districts']:
            base_risk = 0.65
        
        # Rainfall contribution
        rain_factor = 0.0
        thresholds = self.NEPAL_LANDSLIDE_CONFIG['rainfall_thresholds']
        
        if rainfall_24h > thresholds['critical']['24h']:
            rain_factor = 0.45
        elif rainfall_24h > thresholds['high']['24h']:
            rain_factor = 0.30
        elif rainfall_24h > thresholds['medium']['24h']:
            rain_factor = 0.18
        elif rainfall_24h > thresholds['low']['24h']:
            rain_factor = 0.08
        
        # Slope and geology factor (simplified)
        slope_factor = 0.25 if district_info.get('landslide_risk', 3) >= 4 else 0.12
        
        total_risk = min(base_risk + rain_factor + slope_factor, 1.0)
        
        # Determine level
        if total_risk > 0.82:
            level = "CRITICAL"
            action = "EVACUATE_HIGH_RISK_AREAS"
        elif total_risk > 0.65:
            level = "HIGH"
            action = "PREPARE_EVACUATION"
        elif total_risk > 0.45:
            level = "MEDIUM"
            action = "MONITOR_SLOPES"
        else:
            level = "LOW"
            action = "MONITOR"
        
        affected_vdcs = ["High slope areas", "River banks"] if level in ["HIGH", "CRITICAL"] else []
        
        return {
            "district": district,
            "risk_level": level,
            "risk_score": round(total_risk, 2),
            "rainfall_24h": round(rainfall_24h, 1),
            "rainfall_72h": round(rainfall_72h, 1),
            "antecedent_index": round(ari, 1),
            "affected_vdcs": affected_vdcs,
            "estimated_population_at_risk": int(district_info.get('population', 200000) * total_risk * 0.15),
            "recommended_action": action,
            "alert_message_nepali": self._generate_landslide_message(district, level, rainfall_24h)
        }

    def _generate_landslide_message(self, district: str, level: str, rainfall: float) -> str:
        if level == "CRITICAL":
            return f"""🔴 पहिरो तत्काल खतरा!
{district} जिल्लामा अत्यधिक वर्षा ({rainfall}mm) ले पहिरोको उच्च जोखिम।
भिरालो क्षेत्रबाट तुरुन्तै सुरक्षित ठाउँमा जानुहोस्!
NDRRMA: 1162"""
        elif level == "HIGH":
            return f"""🟠 पहिरो चेतावनी
{district} मा पहिरोको खतरा। भिरालो ठाउँबाट टाढा रहनुस्।
वर्षा: {rainfall}mm/२४घण्टा। NDRRMA:1162"""
        else:
            return f"⚠️ {district} मा पहिरो सावधानी अपनाउनुहोस्।"

    async def get_high_risk_zones_geojson(self, db: Session) -> Dict:
        """Return GeoJSON risk map for Nepal"""
        features = []
        for district_info in NEPAL_DISTRICTS[:30]:  # Sample for demo
            risk = await self.calculate_district_landslide_risk(district_info['name_english'], db)
            
            color = "#22c55e" if risk['risk_level'] == "LOW" else \
                    "#eab308" if risk['risk_level'] == "MEDIUM" else \
                    "#f97316" if risk['risk_level'] == "HIGH" else "#ef4444"
            
            features.append({
                "type": "Feature",
                "properties": {
                    "district": district_info['name_english'],
                    "risk_level": risk['risk_level'],
                    "risk_score": risk['risk_score'],
                    "color": color
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [district_info['lon'], district_info['lat']]
                }
            })
        
        return {
            "type": "FeatureCollection",
            "features": features
        }

    async def predict_landslide_risk(self, district: str, hours_ahead: int = 12, db: Session = None) -> Dict:
        return await self.calculate_district_landslide_risk(district, db)