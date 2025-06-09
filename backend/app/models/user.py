from sqlalchemy import Column, Integer, String, Boolean, Enum # 新增 Enum
import enum # Python 原生的 enum 模組

from app.db.base_class import Base

# 定義角色枚舉類型
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user" # 一般使用者

class User(Base):
    __tablename__ = "users"
    email = Column(String(255), unique=True, index=True, nullable=False)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True)
    # is_superuser = Column(Boolean(), default=False) # 可以移除或保留作為最高權限標記

    # 新增 role 欄位
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False) # 預設為一般使用者

