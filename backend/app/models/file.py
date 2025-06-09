# backend/app/models/file.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True, nullable=False) # Original filename
    storage_path = Column(String(255), unique=True, index=True, nullable=False) # Path in S3/MinIO
    file_type = Column(String(100), nullable=True) # MIME type
    size = Column(Integer, nullable=True) # In bytes
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    is_encrypted = Column(Boolean, default=True) # Assuming SSE-S3 by default
    encryption_method = Column(String(50), default="SSE-S3")

    owner = relationship("User")