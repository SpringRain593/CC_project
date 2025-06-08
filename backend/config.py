import os
from dotenv import load_dotenv

load_dotenv()  # 載入 .env

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_NAME = "cloudfs_db"

settings = Settings()

