from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.refresh_token import RefreshToken
from app.models.user import User

def create_refresh_token(
    db: Session, *, user: User, expires_delta: timedelta, token_value: str | None = None
) -> RefreshToken:
    """
    為指定使用者建立並儲存一個新的 Refresh Token。
    """
    if token_value is None:
        token_value = RefreshToken.generate_token()
    
    expires_at = datetime.utcnow() + expires_delta
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=token_value,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    db.refresh(db_refresh_token)
    return db_refresh_token

def get_refresh_token_by_value(db: Session, token_value: str) -> RefreshToken | None:
    """
    根據 token 字串查詢 Refresh Token。
    """
    return db.query(RefreshToken).filter(RefreshToken.token == token_value).first()

def get_active_refresh_token_by_value(db: Session, token_value: str) -> RefreshToken | None:
    """
    根據 token 字串查詢有效的 (未過期且未撤銷的) Refresh Token。
    """
    token = db.query(RefreshToken).filter(RefreshToken.token == token_value).first()
    if token and token.is_active:
        return token
    return None

def revoke_refresh_token(db: Session, token: RefreshToken) -> RefreshToken:
    """
    撤銷一個 Refresh Token。
    """
    if token:
        token.revoked_at = datetime.utcnow()
        db.add(token)
        db.commit()
        db.refresh(token)
    return token

def revoke_all_refresh_tokens_for_user(db: Session, user_id: int) -> int:
    """
    撤銷指定使用者的所有 Refresh Tokens。
    返回被撤銷的 token 數量。
    """
    now = datetime.utcnow()
    updated_count = (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .update({"revoked_at": now}, synchronize_session=False)
    )
    db.commit()
    return updated_count

def delete_expired_refresh_tokens(db: Session) -> int:
    """
    刪除資料庫中所有已過期的 Refresh Tokens。
    返回被刪除的 token 數量。
    (這可以由一個背景任務定期執行)
    """
    now = datetime.utcnow()
    deleted_count = (
        db.query(RefreshToken)
        .filter(RefreshToken.expires_at < now)
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted_count