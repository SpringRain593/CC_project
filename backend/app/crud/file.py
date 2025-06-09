# backend/app/crud/file.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.file import FileMetadata
from app.schemas.file import FileCreate

def create_file_metadata(db: Session, file_in: FileCreate) -> FileMetadata:
    db_file = FileMetadata(
        filename=file_in.filename,
        storage_path=file_in.storage_path,
        file_type=file_in.file_type,
        size=file_in.size,
        owner_id=file_in.owner_id,
        is_encrypted=file_in.is_encrypted,
        encryption_method=file_in.encryption_method
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_file_metadata_by_id(db: Session, file_id: int) -> Optional[FileMetadata]:
    return db.query(FileMetadata).filter(FileMetadata.id == file_id).first()

def get_file_metadata_by_id_and_owner(
    db: Session, file_id: int, owner_id: int
) -> Optional[FileMetadata]:
    return db.query(FileMetadata).filter(FileMetadata.id == file_id, FileMetadata.owner_id == owner_id).first()

def get_files_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[FileMetadata]:
    return db.query(FileMetadata).filter(FileMetadata.owner_id == owner_id).offset(skip).limit(limit).all()

def delete_file_metadata(db: Session, file_id: int) -> Optional[FileMetadata]:
    db_file = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if db_file:
        db.delete(db_file)
        db.commit()
    return db_file # Returns the deleted object or None if not found

def update_file_filename(
    db: Session, file_id: int, new_filename: str, owner_id: Optional[int] = None
) -> Optional[FileMetadata]:
    """
    更新指定檔案的檔案名稱。
    如果提供了 owner_id，則僅當檔案屬於該擁有者時才更新。
    """
    query = db.query(FileMetadata).filter(FileMetadata.id == file_id)
    if owner_id is not None: # 如果是普通使用者操作，則需要驗證擁有權
        query = query.filter(FileMetadata.owner_id == owner_id)
    
    db_file = query.first()
    
    if db_file:
        db_file.filename = new_filename
        db.add(db_file) # 或者 db.merge(db_file)
        db.commit()
        db.refresh(db_file)
    return db_file

def get_all_files(db: Session, owner_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[FileMetadata]:
    """
    獲取所有檔案的列表，如果提供了 owner_id，則按擁有者過濾。
    """
    query = db.query(FileMetadata)
    if owner_id is not None:
        query = query.filter(FileMetadata.owner_id == owner_id)
    return query.order_by(FileMetadata.uploaded_at.desc()).offset(skip).limit(limit).all()
