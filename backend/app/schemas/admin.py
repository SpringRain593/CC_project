# backend/app/schemas/admin.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole # 匯入 UserRole enum

class AdminUserUpdate(BaseModel):
    """
    Schema for an admin to update a user's details.
    All fields are optional.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    # Password update by admin is usually a separate "reset password" flow,
    # so we might not include it here directly for a general update.
    # password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

# 如果您決定將其放入 user.py，則不需要此檔案