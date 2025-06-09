from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings # 引用設定檔
from app.schemas.token import TokenData # Token 承載資料的 Pydantic schema
from app.crud import user as crud_user # 使用者 CRUD 操作
from app.db.session import get_db # 資料庫 session 相依性
from app.models.user import User # 使用者 ORM 模型

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM # "HS256"
JWT_SECRET_KEY = settings.JWT_SECRET_KEY # 您的 JWT 密鑰

# OAuth2PasswordBearer 會從請求的 Authorization 標頭中尋找 Bearer token
# tokenUrl 指向獲取 token 的端點 (您的登入端點)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/access-token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證明文密碼與雜湊後的密碼是否相符"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """產生密碼的雜湊值"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    根據提供的資料和過期時間來建立新的 access token。
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) #
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), # 從 Authorization 標頭獲取 token
    db: Session = Depends(get_db)
) -> User:
    """
    解碼並驗證 access token，返回目前使用者。
    如果 token 無效或使用者不存在，則拋出 HTTPException。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError: # 包括 Token 過期 (ExpiredSignatureError) 或簽名無效等
        raise credentials_exception
    
    user = crud_user.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    獲取目前登入且狀態為 active 的使用者。
    如果使用者 inactive，則拋出 HTTPException。
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user