from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://bipad_user:password@localhost:5432/bipad_sahayak",
        env="DATABASE_URL"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # JWT
    SECRET_KEY: str = Field(default="your-super-secret-key-change-this-in-production", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10080, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Nepal SMS
    SPARROW_SMS_TOKEN: str = Field(default="your-sparrow-sms-token", env="SPARROW_SMS_TOKEN")
    SPARROW_SMS_FROM: str = Field(default="BipadAlert", env="SPARROW_SMS_FROM")
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = Field(default="./firebase-credentials.json", env="FIREBASE_CREDENTIALS_PATH")
    
    # Weather APIs
    OPENWEATHERMAP_API_KEY: str = Field(default="your-openweathermap-key", env="OPENWEATHERMAP_API_KEY")
    TOMORROW_IO_API_KEY: str = Field(default="your-tomorrow-io-key", env="TOMORROW_IO_API_KEY")
    
    # NASA
    NASA_EARTHDATA_TOKEN: str = Field(default="your-nasa-token", env="NASA_EARTHDATA_TOKEN")
    
    # Copernicus
    COPERNICUS_USERNAME: str = Field(default="your-copernicus-email", env="COPERNICUS_USERNAME")
    COPERNICUS_PASSWORD: str = Field(default="your-copernicus-password", env="COPERNICUS_PASSWORD")
    
    # Mapbox
    MAPBOX_API_KEY: str = Field(default="your-mapbox-key", env="MAPBOX_API_KEY")
    
    # WhatsApp
    WHATSAPP_API_TOKEN: str = Field(default="your-whatsapp-token", env="WHATSAPP_API_TOKEN")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="your-openai-key", env="OPENAI_API_KEY")
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str = Field(default="your-aws-key", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="your-aws-secret", env="AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME: str = Field(default="bipad-sahayak-photos", env="AWS_BUCKET_NAME")
    AWS_REGION: str = Field(default="ap-south-1", env="AWS_REGION")
    
    # Sentry
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # Nepal Specific
    NEPAL_TIMEZONE: str = Field(default="Asia/Kathmandu", env="NEPAL_TIMEZONE")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://bipadsahayak.com.np"],
        env="ALLOWED_ORIGINS"
    )
    
    # DHM & NDRRMA
    DHM_API_KEY: str = Field(default="request-from-dhm-gov-np", env="DHM_API_KEY")
    NDRRMA_API_KEY: str = Field(default="request-from-ndrrma-gov-np", env="NDRRMA_API_KEY")
    
    # Admin
    ADMIN_PHONE: str = Field(default="+9779800000000", env="ADMIN_PHONE")
    ALERT_APPROVAL_REQUIRED: bool = Field(default=True, env="ALERT_APPROVAL_REQUIRED")
    
    # Limits
    MAX_SMS_PER_ALERT: int = Field(default=10000, env="MAX_SMS_PER_ALERT")
    SMS_RATE_LIMIT_PER_SECOND: int = Field(default=50, env="SMS_RATE_LIMIT_PER_SECOND")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

settings = Settings()