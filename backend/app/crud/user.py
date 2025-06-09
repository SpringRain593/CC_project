from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.admin import AdminUserUpdate
from app.models.user import User, UserRole # 假設 UserRole 在 models.user 中
from app.schemas.user import UserCreate, AdminUserCreate
from app.core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> User | None:
    """透過電子郵件查詢使用者"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    """透過使用者名稱查詢使用者"""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """建立新使用者"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=UserRole.USER  # 新註冊使用者預設為 USER 角色，或根據需求調整
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    驗證使用者。
    如果驗證成功，返回使用者物件；否則返回 None。
    """
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not user.is_active: # 可以選擇是否檢查使用者是否啟用
        return None # 或者拋出特定錯誤
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    根據 User ID 獲取使用者。
    """
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    獲取使用者列表 (支援分頁)。
    """
    return db.query(User).offset(skip).limit(limit).all()

def update_user_by_admin(db: Session, user_to_update: User, user_in: AdminUserUpdate) -> User:
    """
    由管理員更新使用者的資訊。
    `user_to_update` 應該是從資料庫中獲取的 User ORM 物件。
    `user_in` 是包含更新資料的 Pydantic schema。
    """
    update_data = user_in.model_dump(exclude_unset=True) # Pydantic v2
    # 如果是 Pydantic v1: update_data = user_in.dict(exclude_unset=True)

    if "email" in update_data:
        user_to_update.email = update_data["email"]
    if "username" in update_data: # 通常不建議管理員隨意更改 username，除非有充分理由
        user_to_update.username = update_data["username"]
    if "is_active" in update_data:
        user_to_update.is_active = update_data["is_active"]
    if "role" in update_data:
        user_to_update.role = update_data["role"]
    
    # 注意：不直接處理密碼更新，那通常是獨立的 "重設密碼" 流程。
    # 如果要支援管理員修改密碼 (不推薦直接設定明文密碼):
    # if "password" in update_data and update_data["password"]:
    #     hashed_password = get_password_hash(update_data["password"])
    #     user_to_update.hashed_password = hashed_password

    db.add(user_to_update)
    db.commit()
    db.refresh(user_to_update)
    return user_to_update

def remove_user(db: Session, user_id: int) -> Optional[User]:
    """
    刪除一個使用者。
    返回被刪除的使用者物件，如果找不到則返回 None。
    注意：實際應用中，刪除使用者需要謹慎處理其關聯資料 (例如檔案)。
    這裡僅作簡單刪除。
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # 在刪除使用者之前，您可能需要處理該使用者上傳的檔案：
        # 1. 將檔案標記為孤立
        # 2. 轉移檔案擁有權給某個系統帳戶
        # 3. 級聯刪除檔案 (如果業務邏輯允許)
        # 這裡我們暫不處理檔案，僅刪除使用者記錄。
        db.delete(user)
        db.commit()
    return user

def is_username_taken(db: Session, username: str) -> bool:
    """
    檢查使用者名稱是否已被占用。
    """
    return db.query(User).filter(User.username == username).first() is not None

def update_current_user_username(db: Session, user_to_update: User, new_username: str) -> Optional[User]:
    """
    更新目前登入使用者的 username。
    `user_to_update` 是從資料庫中獲取的 User ORM 物件。
    """
    # 檢查新的 username 是否與目前的不同，且是否已被其他人使用
    if new_username != user_to_update.username and is_username_taken(db, username=new_username):
        return None # 表示 username 已被占用

    user_to_update.username = new_username
    db.add(user_to_update)
    db.commit()
    db.refresh(user_to_update)
    return user_to_update

def update_user_password(db: Session, *, user: User, new_password: str) -> None:
    """更新指定使用者的密碼"""
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()

def create_user_by_admin(db: Session, user_in: AdminUserCreate) -> User:
    """由 Admin 建立新使用者，可以指定角色和啟用狀態"""
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        role=user_in.role,
        is_active=user_in.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user