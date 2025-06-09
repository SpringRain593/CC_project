from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # 引用 settings 中的 DATABASE_URL

# DATABASE_URL 格式範例 (MySQL):
# "mysql+mysqlconnector://user:password@host:port/database_name"
# "mysql+pymysql://user:password@host:port/database_name"

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()