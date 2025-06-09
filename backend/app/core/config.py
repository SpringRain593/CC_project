from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List

class Settings(BaseSettings):
    DATABASE_URL: str
    
    PROJECT_NAME: str
    VERSION: str
    ALLOW_ORIGINS: List[str] = ["*"]
    
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    MINIO_ENDPOINT_URL: Optional[str] = None
    MINIO_ROOT_USER: Optional[str] = None      # <--- 新增
    MINIO_ROOT_PASSWORD: Optional[str] = None  # <--- 新增
    MINIO_SERVER_URL: Optional[str] = None

    STORAGE_PROVIDER: str = "s3"
    # --- AWS S3 Settings ---
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None # For AWS Academy temporary credentials
    AWS_REGION: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None

    # --- Presigned URL Settings ---
    PRESIGNED_URL_EXPIRE_SECONDS: int = 3600 # Default 1 hour
    PRESIGNED_URL_EXPIRE_SECONDS_MAX: int = 86400 # Maximum 24 hours

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    CLOUDWATCH_LOG_GROUP: Optional[str] = None
    CLOUDWATCH_LOG_STREAM: Optional[str] = None
    
    # --- 新增 Refresh Token 相關設定 ---
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # Refresh Token 預設 7 天過期
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    REFRESH_TOKEN_COOKIE_PATH: str = "/"
    REFRESH_TOKEN_COOKIE_DOMAIN: Optional[str] = None # None 表示僅限當前網域
    REFRESH_TOKEN_COOKIE_SECURE: bool = True # 在生產環境中應為 True (僅限 HTTPS)
    REFRESH_TOKEN_COOKIE_HTTPONLY: bool = True # 強烈建議為 True
    REFRESH_TOKEN_COOKIE_SAMESITE: str = "lax" # "lax" 或 "strict"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # <--- 新增這一行


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()