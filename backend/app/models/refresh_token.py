import secrets
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timedelta

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # 關聯到 User 模型
    token = Column(String(512), unique=True, index=True, nullable=False) # Refresh Token 字串
    expires_at = Column(DateTime, nullable=False) # 過期時間
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True) # 標記為已撤銷的時間

    user = relationship("User") # 建立與 User 的關聯

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and datetime.utcnow() < self.expires_at

    @staticmethod
    def generate_token(length: int = 128) -> str:
        return secrets.token_urlsafe(length)