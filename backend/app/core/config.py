"""
Core configuration for MissYak Social API.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "MissYak Social API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 1 week

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LiveKit
    LIVEKIT_API_KEY: str
    LIVEKIT_API_SECRET: str
    LIVEKIT_WS_URL: str

    # AWS S3 / Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "eu-central-1"
    S3_BUCKET_NAME: str = "missyak-social"
    S3_ENDPOINT_URL: str = ""  # For S3-compatible services

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"

    # CORS
    CORS_ORIGINS: str = "http://localhost:19006"
    ALLOWED_HOSTS: str = "*"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def allowed_image_types_list(self) -> List[str]:
        return [t.strip() for t in self.ALLOWED_IMAGE_TYPES.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
