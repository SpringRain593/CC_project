# backend/app/schemas/file.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FileBase(BaseModel):
    filename: str
    file_type: Optional[str] = None
    size: Optional[int] = None

class FileCreate(FileBase): # Used when creating metadata in DB
    storage_path: str
    owner_id: int
    is_encrypted: bool = True
    encryption_method: str = "SSE-S3"

class FileUpdate(BaseModel): # For potential future use (e.g., renaming)
    filename: Optional[str] = None

class FileRead(FileBase):
    id: int
    storage_path: str # Usually not exposed directly to user if using presigned URLs for access
    owner_id: int
    uploaded_at: datetime
    is_encrypted: bool
    encryption_method: str

    class Config:
        from_attributes = True


class FileRename(BaseModel):
    new_filename: str = Field(..., min_length=1, max_length=255) # 新的檔案名稱，並加上基本驗證

class PresignedUrlResponse(BaseModel):
    url: str
    filename: str # Include original filename for convenience
    method: str = "GET" # The HTTP method this URL is for
    expires_at: Optional[datetime] = None # Optional: Calculate and provide actual expiry time