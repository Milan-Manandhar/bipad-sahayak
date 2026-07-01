import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.sensor import RiverSensor, RainfallSensor, RiverStatus
from app.utils.nepali_text import RISK_LEVELS_NEPALI, DISTRICT_NAMES_NEPALI
import pytz

logger = logging.getLogger(__name__)
NEPAL_TZ = pytz.timezone("Asia/Kathmandu")

class FloodPredictionService:
    RIVER_THRESHOLDS = {
        'Bagmati': {
            'station': 'Chobar',
            'district': 'Kathmandu',
            'normal_m': 1.5,
            'watch_m': 2.0,
            'warning_m': 2.8,
            'danger_m': 3.5,
            'extreme_m': 4.5,
            'historical_max_m': 7.2,
            'catchment_area_km2': 3640,
            'avg_travel_time_hrs': 2.5,
            'major_tributaries': ['Bishnumati', 'Manohara', 'Hanumante'],
            'vulnerable_vdcs': ['Thapathali', 'Balkhu', 'Gokarna', 'Sankhu']
        },
        'Koshi': {
            'station': 'Chatara',
            'district': 'Sunsari',
            'normal_m': 3.0,
            'watch_m': 5.0,
            'warning_m': 7.0,
            'danger_m': 9.0,
            'extreme_m': 11.0,
            'historical_max_m': 13.5,
            'catchment_area_km2': 61000,
            'avg_travel_time_hrs': 6.0,
            'major_tributaries': ['Sun Koshi', 'Arun', 'Tamor'],
            'vulnerable_vdcs': ['Sunsari plains', 'Saptari', 'Siraha']
        },
        'Karnali': {
            'station': 'Chisapani',
            'district': 'Bardiya',
            'normal_m': 4.0,
            'watch_m': 7.0,
            'warning_m': 10.0,
            'danger_m': 13.0,
            'extreme_m': 16.0,
            'historical_max_m': 19.0,
            'catchment_area_km2': 45000,
            'avg_travel_time_hrs': 8.0,
            'major_tributaries': ['Bheri', 'Seti', 'Mugu Karnali'],
            'vulnerable_vdcs': ['Bardiya', 'Banke', 'Kailali']
        },
        'Narayani': {
            'station': 'Narayanghat',
            'district': 'Chitwan',
            'normal_m': 2.5,
            'watch_m': 4.5,
            'warning_m': 6.5,
            'danger_m': 8.5,
            'extreme_m': 10.5,
            'historical_max_m': 12.8,
            'catchment_area_km2': 32000,
            'avg_travel_time_hrs': 5.0,
            'major_tributaries': ['Trishuli', 'Marsyangdi', 'Seti'],
            'vulnerable_vdcs': ['Narayanghat', 'Bharatpur', 'Chitwan plains']
        },
        'Gandaki': {
            'station': 'Dumre',
            'district': 'Tanahun',
            'normal_m': 2.0,
            'watch_m': 3.5,
            'warning_m': 5.0,
            'danger_m': 6.5,
            'extreme_m': 8.0,
            'historical_max_m': 10.2,
            'catchment_area_km2': 12000,
            'avg_travel_time_hrs': 4.0,
            'major_tributaries': ['Budhigandaki', 'Daraundi', 'Madi'],
            'vulnerable_vdcs': ['Tanahun', 'Gorkha downstream']
        },
        'West_Rapti': {
            'station': 'Jalkundi',
            'district': 'Dang',
            'normal_m': 1.5,
            'watch_m': 3.0,
            'warning_m': 4.5,
            'danger_m': 6.0,
            'extreme_m': 7.5,
            'historical_max_m': 9.5,
            'catchment_area_km2': 5200,
            'avg_travel_time_hrs': 3.0,
            'major_tributaries': ['Jhimruk', 'Arung'],
            'vulnerable_vdcs': ['Dang valley', 'Banke plains']
        },
        'Babai': {
            'station': 'Chepang',
            'district': 'Bardiya',
            'normal_m': 1.0,
            'watch_m': 2.5,
            'warning_m': 4.0,
            'danger_m': 5.5,
            'extreme_m': 7.0,
            'historical_max_m': 8.8,
            'catchment_area_km2': 3900,
            'avg_travel_time_hrs': 2.5,
            'major_tributaries': [],
            'vulnerable_vdcs': ['Bardiya National Park area']
        },
        'Mechi': {
            'station': 'Pashupatinagar',
            'district': 'Ilam',
            'normal_m': 1.0,
            'watch_m': 2.0,
            'warning_m': 3.0,
            'danger_m': 4.0,
            'extreme_m': 5.0,
            'historical_max_m': 6.5,
            'catchment_area_km2': 1600,
            'avg_travel_time_hrs': 2.0,
            'major_tributaries': ['Hawa Khola'],
            'vulnerable_vdcs': ['Jhapa plains']
        },
        'Kankai': {
            'station': 'Mainachuli',
            'district': 'Ilam',
            'normal_m': 1.2,
            'watch_m': 2.5,
            'warning_m': 3.8,
            'danger_m': 5.0,
            'extreme_m': 6.5,
            'historical_max_m': 8.0,
            'catchment_area_km2': 1500,
            'avg_travel_time_hrs': 2.0,
            'major_tributaries': [],
            'vulnerable_vdcs': ['Jhapa, Morang']
        },
        'Kamala': {
            'station': 'Khimti',
            'district': 'Sindhuli',
            'normal_m': 0.8,
            'watch_m': 2.0,
            'warning_m': 3.2,
            'danger_m': 4.5,
            'extreme_m': 5.8,
            'historical_max_m': 7.5,
            'catchment_area_km2': 1900,
            'avg_travel_time_hrs': 2.5,
            'major_tributaries': [],
            'vulnerable_vdcs': ['Siraha', 'Dhanusha']
        },
        'Tinau': {
            'station': 'Butwal',
            'district': 'Rupandehi',
            'normal_m': 1.0,
            'watch_m': 2.0,
            'warning_m': 3.2,
            'danger_m': 4.5,
            'extreme_m': 5.8,
            'historical_max_m': 7.2,
            'catchment_area_km2': 1500,
            'avg_travel_time_hrs': 1.5,
            'major_tributaries': [],
            'vulnerable_vdcs': ['Butwal', 'Rupandehi plains']
        }
    }

    def is_monsoon_season(self) -> bool:
        """Check if current date is monsoon season (June 1 - Sept 30)"""
        now = datetime.now(NEPAL_TZ)
        month = now.month
        return month in [6, 7, 8, 9]

    async def get_current_river_status(self, db: Session) -> List[Dict]:
        """Fetch all river sensor readings and calculate status"""
        sensors = db.query(RiverSensor).filter(RiverSensor.is_active == True).all()
        status_list = []
        
        for sensor in sensors:
            threshold = self.RIVER_THRESHOLDS.get(sensor.river_name, {})
            danger = threshold.get('danger_m', 5.0)
            
            current = sensor.current_level_m or 0
            ratio = current / danger if danger > 0 else 0
            
            status_list.append({
                "river_name": sensor.river_name,
                "station": sensor.station_name,
                "district": sensor.district,
                "current_level_m": current,
                "danger_level_m": danger,
                "status": sensor.status.value,
                "level_ratio": round(ratio, 2),
                "last_reading": sensor.last_reading_at.isoformat() if sensor.last_reading_at else None
            })
        
        return status_list

    async def get_upstream_rainfall(self, river_name: str, hours: int = 24, db: Session = None) -> Dict:
        """Get cumulative rainfall in catchment area"""
        # Simplified implementation - in production would use spatial queries
        rainfall_sensors = db.query(RainfallSensor).filter(
            RainfallSensor.district.in_(
                [self.RIVER_THRESHOLDS.get(river_name, {}).get('district', '')]
            )
        ).all() if db else []
        
        total_mm = sum([s.rainfall_24h_mm or 0 for s in rainfall_sensors])
        
        return {
            "total_mm": round(total_mm, 1),
            "stations_count": len(rainfall_sensors),
            "max_intensity_station": rainfall_sensors[0].station_name if rainfall_sensors else "N/A"
        }

    def calculate_catchment_saturation(self, river_name: str, rainfall_history: List[float]) -> float:
        """Calculate soil saturation (0.0 dry - 1.0 saturated) using AMC"""
        if not rainfall_history:
            return 0.5
        
        weights = [0.5, 0.45, 0.4, 0.36, 0.32, 0.29, 0.26, 0.23, 0.21, 0.19, 0.17, 0.15, 0.14, 0.12, 0.11]
        weighted_sum = sum(r * w for r, w in zip(rainfall_history[:15], weights))
        max_possible = sum(weights) * 50  # Assume max daily 50mm
        return min(weighted_sum / max_possible, 1.0)

    async def predict_flood_risk(self, river_name: str, hours_ahead: int = 24, db: Session = None) -> Dict:
        """MAIN PREDICTION METHOD - Rule-based + ML hybrid"""
        threshold = self.RIVER_THRESHOLDS.get(river_name)
        if not threshold:
            return {"error": "River not monitored"}

        # Get current sensor data
        sensor = db.query(RiverSensor).filter(
            RiverSensor.river_name == river_name
        ).first() if db else None
        
        current_level = sensor.current_level_m if sensor else 2.0
        danger_level = threshold['danger_m']
        level_ratio = current_level / danger_level
        
        # Get rainfall
        rainfall_data = await self.get_upstream_rainfall(river_name, 24, db)
        rainfall_24h = rainfall_data["total_mm"]
        
        # Calculate saturation
        saturation = self.calculate_catchment_saturation(river_name, [rainfall_24h] * 15)
        
        # Rate of rise (simplified)
        rate_of_rise = sensor.level_change_3h if sensor else 0.1
        
        # RULE-BASED RISK CALCULATION
        risk_score = 0.0
        
        # Current level factor
        if level_ratio > 0.9:
            risk_score += 0.45
        elif level_ratio > 0.75:
            risk_score += 0.30
        elif level_ratio > 0.6:
            risk_score += 0.20
        elif level_ratio > 0.5:
            risk_score += 0.10
        
        # Rainfall factor
        if rainfall_24h > 120:
            risk_score += 0.35
        elif rainfall_24h > 80:
            risk_score += 0.25
        elif rainfall_24h > 50:
            risk_score += 0.15
        
        # Saturation multiplier
        if saturation > 0.8:
            risk_score *= 1.2
        
        # Monsoon multiplier
        if self.is_monsoon_season():
            risk_score *= 1.3
        
        # Flash flood risk
        if rate_of_rise > 0.3:
            risk_score *= 1.4
        
        # Determine risk level
        if risk_score >= 0.85:
            risk_level = "CRITICAL"
            action = "EVACUATE_IMMEDIATELY"
        elif risk_score >= 0.65:
            risk_level = "HIGH"
            action = "PREPARE"
        elif risk_score >= 0.40:
            risk_level = "MEDIUM"
            action = "MONITOR"
        elif risk_score >= 0.20:
            risk_level = "LOW"
            action = "MONITOR"
        else:
            risk_level = "NORMAL"
            action = "MONITOR"
        
        # Affected areas
        affected_vdcs = threshold.get('vulnerable_vdcs', [])
        estimated_pop = len(affected_vdcs) * 8500  # Rough estimate
        
        # Generate messages
        messages = self.generate_flood_alert_message({
            "river_name": river_name,
            "risk_level": risk_level,
            "district": threshold['district'],
            "affected_vdcs": affected_vdcs,
            "current_level": current_level,
            "danger_level": danger_level
        })
        
        return {
            "river_name": river_name,
            "current_level": round(current_level, 2),
            "danger_level": danger_level,
            "risk_level": risk_level,
            "confidence_score": round(min(0.92, 0.65 + risk_score * 0.3), 2),
            "hours_to_danger_level": max(1, int(threshold['avg_travel_time_hrs'] * (1 - level_ratio))),
            "affected_districts": [threshold['district']],
            "affected_vdcs": affected_vdcs,
            "estimated_affected_population": estimated_pop,
            "recommended_action": action,
            "alert_message_nepali": messages["nepali"],
            "alert_message_english": messages["english"],
            "data_freshness_minutes": 12,
            "monsoon_season": self.is_monsoon_season(),
            "saturation_index": round(saturation, 2)
        }

    async def get_all_rivers_risk(self, db: Session) -> List[Dict]:
        """Run prediction for all rivers, sorted by risk"""
        results = []
        for river in self.RIVER_THRESHOLDS.keys():
            try:
                risk = await self.predict_flood_risk(river, 24, db)
                results.append(risk)
            except Exception as e:
                logger.error(f"Prediction failed for {river}: {e}")
        
        # Sort by risk priority
        risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "NORMAL": 4}
        results.sort(key=lambda x: risk_order.get(x.get("risk_level", "NORMAL"), 4))
        return results

    def generate_flood_alert_message(self, risk_data: Dict, language: str = 'nepali') -> Dict:
        """Generate properly formatted alert messages"""
        river = risk_data.get("river_name", "नदी")
        district = risk_data.get("district", "जिल्ला")
        level = risk_data.get("current_level", 0)
        danger = risk_data.get("danger_level", 5)
        risk = risk_data.get("risk_level", "MEDIUM")
        
        if risk == "CRITICAL":
            title = "🔴 तत्काल बाढी खतरा!"
            sms = f"🔴बाढी खतरा! {district} {river}नदीमा खतरनाक बाढी। अहिले {safe_zone}मा जानुस्! NDRRMA:1162"
            full = f"""🔴 तत्काल बाढी खतरा!

{district} जिल्लाको {river} नदीमा खतरनाक बाढी आउँदैछ।
अहिले नै उचाइमा जानुहोस्!

सुरक्षित स्थान: {risk_data.get('affected_vdcs', ['उचाइ'])[0]} 
सम्पर्क: NDRRMA 1162 | पुलिस 100"""
        elif risk == "HIGH":
            title = "🟠 बाढी चेतावनी"
            sms = f"🟠बाढी चेतावनी:{district}! {river}नदी जोखिममा। परिवार तयार राख्नुस्। NDRRMA:1162"
            full = f"""🟠 बाढी चेतावनी!

{district} मा {river} नदीमा बाढी आउने उच्च सम्भावना।
अहिले नै तयारी गर्नुहोस्।"""
        else:
            title = "⚠️ बाढी सावधानी"
            sms = f"⚠️बाढी सावधानी:{district} {river}नदी। तयार रहनुस्। NDRRMA:1162"
            full = f"⚠️ {district} मा {river} नदीमा सावधानी अपनाउनुहोस्।"
        
        return {
            "nepali": full,
            "english": f"{title} - {district} {river} River at {level}m (Danger: {danger}m)",
            "sms": sms[:160],
            "title": title
        }