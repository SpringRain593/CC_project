# backend/app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole # 匯入 User 和 UserRole
from app.schemas.user import UserRead, AdminUserCreate, AdminResetPassword # 用於回應
from app.schemas.admin import AdminUserUpdate # 用於管理員更新使用者
from app.crud import user as crud_user

from app.schemas.user import UserUpdateUsername # 用於更新使用者名稱
from app.schemas.user import UserUpdatePassword # 
import logging

logger = logging.getLogger(__name__) # 設定 logger



router = APIRouter()

def require_admin_role(current_user: User = Depends(get_current_active_user)):
    """
    相依性：要求目前使用者必須是 ADMIN 角色。
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges (Admin role required)",
        )
    return current_user

def require_manager_or_admin_role(current_user: User = Depends(get_current_active_user)):
    """
    相依性：要求目前使用者必須是 MANAGER 或 ADMIN 角色。
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges (Manager or Admin role required)",
        )
    return current_user

@router.get("/", response_model=List[UserRead], dependencies=[Depends(require_admin_role)])
async def read_users_by_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # current_admin: User = Depends(require_admin_role) # 已透過 dependencies 注入並檢查
):
    """
    (Admin only) 獲取使用者列表。
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_admin_role)])
async def read_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    # current_admin: User = Depends(require_admin_role)
):
    """
    (Admin only) 根據 ID 獲取特定使用者資訊。
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(require_admin_role)])
async def update_user_by_admin_endpoint(
    user_id: int,
    user_in: AdminUserUpdate, # 從請求主體獲取更新資料
    db: Session = Depends(get_db),
    # current_admin: User = Depends(require_admin_role)
):
    """
    (Admin only) 更新使用者資訊 (例如角色、啟用狀態)。
    """
    user_to_update = crud_user.get_user(db, user_id=user_id)
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # 防止管理員意外修改自己的角色或把自己設為非啟用 (可以加入此邏輯)
    # current_admin_user = current_admin # 如果上面沒有取消註解
    # if user_to_update.id == current_admin_user.id and \
    #    (user_in.role != UserRole.ADMIN or user_in.is_active is False):
    #     raise HTTPException(status_code=400, detail="Admin users cannot demote themselves or deactivate their own account this way.")

    updated_user = crud_user.update_user_by_admin(db=db, user_to_update=user_to_update, user_in=user_in)
    return updated_user

@router.delete("/{user_id}", response_model=UserRead, dependencies=[Depends(require_admin_role)])
async def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin_role) # 確保是 Admin 操作
):
    """
    (Admin only) 刪除使用者。
    注意：此操作不會處理使用者已上傳的檔案，需要額外邏輯處理。
    """
    if user_id == current_admin.id: # 防止管理員刪除自己
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Administrators cannot delete their own account.")

    user_to_delete = crud_user.remove_user(db, user_id=user_id)
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_to_delete # 回傳被刪除的使用者資訊

@router.patch("/users/me/username", response_model=UserRead)
async def update_own_username(
    user_update_data: UserUpdateUsername, # 接收包含新 username 的請求主體
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # 獲取目前登入的使用者
):
    """
    更新目前登入使用者自己的 username。
    """
    new_username = user_update_data.username
    logger.info(f"User {current_user.username} (ID: {current_user.id}) attempting to update username to '{new_username}'")

    if new_username == current_user.username:
        # 如果新舊名稱相同，可以選擇直接返回成功或提示無需更改
        # 這裡我們直接返回，因為沒有實際變更
        return current_user

    updated_user = crud_user.update_current_user_username(
        db=db, user_to_update=current_user, new_username=new_username
    )

    if not updated_user:
        logger.warning(f"Failed to update username for user {current_user.username} to '{new_username}'. New username likely taken.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 Conflict 更適合表示資源衝突
            detail="Username already taken or update failed.",
        )
    
    logger.info(f"User ID: {current_user.id} successfully updated username from '{current_user.username}' to '{updated_user.username}'")
    return updated_user

@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_own_password(
    password_data: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    更新目前使用者自己的密碼。
    """
    # 驗證舊密碼是否正確
    if not crud_user.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
    
    # 檢查新密碼和確認密碼是否相符
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation password do not match",
        )

    # 更新密碼
    crud_user.update_user_password(db=db, user=current_user, new_password=password_data.new_password)
    
    # HTTP 204 不需要回傳 body
    return

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_role)])
async def create_user_as_admin(
    user_in: AdminUserCreate,
    db: Session = Depends(get_db),
):
    """
    (Admin only) 建立新使用者，可指定角色。
    """
    # 檢查 email 和 username 是否已被註冊
    if crud_user.get_user_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if crud_user.get_user_by_username(db, username=user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user = crud_user.create_user_by_admin(db=db, user_in=user_in)
    return user

@router.patch("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_role)])
async def reset_password_by_admin(
    user_id: int,
    password_data: AdminResetPassword,
    db: Session = Depends(get_db),
):
    """
    (Admin only) 重設指定使用者的密碼。
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    crud_user.update_user_password(db=db, user=user, new_password=password_data.new_password)
    return