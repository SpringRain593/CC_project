from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# 從您的 models 檔案中匯入 UserRole
# 假設 app/models/user.py 中有 UserRole enum 的定義
from app.models.user import UserRole # 或者如果您想避免跨層匯入，可以在此重新定義

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserInDBBase(UserBase):
    id: int
    is_active: bool = True
    role: UserRole

    class Config:
        # Pydantic V2 onwards, orm_mode is now from_attributes
        from_attributes = True # 允許從 ORM 模型直接轉換

class UserRead(UserInDBBase):
    # UserRead 繼承 UserInDBBase，目前沒有額外欄位
    # 如果需要，可以在這裡添加更多僅供讀取的欄位
    pass

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None # 允許更新密碼
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class UserUpdateUsername(BaseModel): # <--- 新增這個 Schema
    username: str = Field(..., min_length=3, max_length=100) # 新的使用者名稱，加上驗證
    
class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)
    confirm_password: str
    
class AdminUserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER
    is_active: bool = True
    
class AdminResetPassword(BaseModel):
    new_password: str = Field(..., min_length=6)