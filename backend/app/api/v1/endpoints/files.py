# backend/app/api/v1/endpoints/files.py
from fastapi import (
    APIRouter, Depends, HTTPException,
    status, UploadFile, File as FastAPIFile, Query
)
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid # For generating unique filenames in S3
import logging

from app.db.session import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.user import UserRole # Assuming UserRole is an Enum in your models
from app.schemas.file import FileCreate, FileRead, PresignedUrlResponse, FileRename
from app.crud import file as crud_file
from app.services.storage_interface import StorageInterface
from app.dependencies import get_storage_service # Import the dependency
from app.core.config import settings
from app.api.v1.endpoints.users import require_manager_or_admin_role
from app.crud import user as crud_user
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=FileRead, status_code=status.HTTP_201_CREATED)
async def upload_file_endpoint(
    uploaded_file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    storage_service: StorageInterface = Depends(get_storage_service)
):
    if not uploaded_file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided.")

    # Sanitize filename and create a unique storage path
    sanitized_filename = "".join(c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in uploaded_file.filename)
    storage_path = f"{current_user.id}/{uuid.uuid4()}_{sanitized_filename}"

    # --- Get file size and content_type BEFORE consuming the file stream for upload ---
    # Read the entire file content into memory or a temporary file on disk first
    # This is important because uploaded_file.file (SpooledTemporaryFile) can only be read once reliably.
    
    # Option 1: Read into a BytesIO buffer (for moderately sized files)
    # from io import BytesIO
    # file_content_buffer = BytesIO()
    # await uploaded_file.seek(0) # Ensure pointer is at the beginning
    # shutil.copyfileobj(uploaded_file.file, file_content_buffer)
    # file_size = file_content_buffer.tell()
    # file_content_buffer.seek(0) # Reset buffer pointer for S3 upload

    # Option 2: Get size first, then reset for S3 (might be risky if file is spooled to disk and closed)
    # This was the problematic approach. Let's improve it by reading first.

    # Safer approach: Determine size by reading the stream.
    # For UploadFile, a robust way to get size is to read it.
    # However, if we read it here, we need to ensure the S3 upload function can re-read it
    # or we pass the read content.
    # Let's get the size from the UploadFile object itself if possible, or by reading its contents.
    # The most robust way is to read the file content once.

    try:
        # Read the file content. Note: This loads the entire file into memory.
        # For very large files, consider streaming or saving to a temp disk file first.
        await uploaded_file.seek(0) # Ensure we start from the beginning
        file_bytes = await uploaded_file.read()
        file_size = len(file_bytes) # Get size from the read bytes
        
        # Now that we have the content in `file_bytes`, we need to provide a file-like
        # object for this content to the S3 upload function.
        from io import BytesIO
        file_content_for_s3 = BytesIO(file_bytes)

        # Upload to S3 (or MinIO via interface)
        actual_storage_path = storage_service.upload_file(
            file_content=file_content_for_s3, # Pass the BytesIO object
            destination_path=storage_path,
            content_type=uploaded_file.content_type
        )
        
        # Create metadata in DB
        file_meta_in = FileCreate(
            filename=uploaded_file.filename, # Store original filename
            storage_path=actual_storage_path, # Path in S3
            file_type=uploaded_file.content_type,
            size=file_size, # Use the size obtained before S3 upload
            owner_id=current_user.id,
        )
        db_file_meta = crud_file.create_file_metadata(db=db, file_in=file_meta_in)
        return db_file_meta
        
    except IOError as e:
        logger.error(f"IOError during file processing or upload for user {current_user.id}, file {uploaded_file.filename}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not process or upload file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during file upload for user {current_user.id}, file {uploaded_file.filename}: {e}", exc_info=True)
        # Consider more specific error handling or rollback if S3 upload succeeded but DB failed.
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during file upload.")
    finally:
        # Ensure the uploaded file (SpooledTemporaryFile) is closed if it's not already
        # await uploaded_file.close() # Usually FastAPI handles this, but can be explicit.
        # If using BytesIO, it's good practice to close it too, though GC will handle it.
        if 'file_content_for_s3' in locals() and file_content_for_s3:
            file_content_for_s3.close()


@router.get("/", response_model=List[FileRead])
async def list_user_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    files = crud_file.get_files_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return files


@router.post("/{file_id}/generate-share-link", response_model=PresignedUrlResponse)
async def generate_file_share_link(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    storage_service: StorageInterface = Depends(get_storage_service),
    expire_seconds: Optional[int] = None # Allow custom expiry via query param or body
):
    file_meta = crud_file.get_file_metadata_by_id(db, file_id=file_id)

    if not file_meta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    # Permission Check: User must own the file or be an admin/manager
    if file_meta.owner_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]: # Assuming UserRole enum
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to share this file.")

    expiration = expire_seconds if expire_seconds is not None else settings.PRESIGNED_URL_EXPIRE_SECONDS
    
    if expiration > settings.PRESIGNED_URL_EXPIRE_SECONDS_MAX:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expiration time cannot exceed {settings.PRESIGNED_URL_EXPIRE_SECONDS_MAX} seconds."
        )
    
    presigned_url = storage_service.generate_presigned_url(
        storage_path=file_meta.storage_path,
        expiration_seconds=expiration,
        http_method="GET",
        download_filename=file_meta.filename # Optional: Specify the filename for download
    )

    if not presigned_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate share link.")
    
    return PresignedUrlResponse(url=presigned_url, filename=file_meta.filename)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    storage_service: StorageInterface = Depends(get_storage_service)
):
    file_meta = crud_file.get_file_metadata_by_id(db, file_id=file_id)

    if not file_meta:
        # 保持不變：找不到檔案直接回 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    # 1. 檔案擁有者本人可以刪除
    # 2. Manager 或 Admin 角色的使用者也可以刪除
    if file_meta.owner_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this file.")

    try:
        # 1. Delete from S3
        storage_service.delete_file(storage_path=file_meta.storage_path)
        # 2. Delete metadata from DB
        crud_file.delete_file_metadata(db, file_id=file_id)
        # No content to return on 204
    except IOError as e:
        logger.error(f"IOError during file deletion (S3 part) for file_id {file_id}: {e}")
        # If S3 deletion fails, we might not want to delete the DB record yet.
        # Or, log it and proceed, depending on desired consistency.
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not delete file from storage: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during file deletion for file_id {file_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during file deletion.")
    
@router.patch("/{file_id}/rename", response_model=FileRead)
async def rename_file_endpoint(
    file_id: int,
    file_rename_data: FileRename, # 接收包含 new_filename 的請求主體
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    重新命名檔案 (僅修改資料庫中的 filename 元數據)。
    檔案擁有者或 ADMIN/MANAGER 角色的使用者可以執行此操作。
    """
    logger.info(f"User {current_user.username} (ID: {current_user.id}, Role: {current_user.role}) attempting to rename file ID: {file_id} to '{file_rename_data.new_filename}'")

    # 檢查檔案是否存在
    file_to_rename = crud_file.get_file_metadata_by_id(db, file_id=file_id)
    if not file_to_rename:
        logger.warning(f"File ID {file_id} not found for renaming by user {current_user.username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # 權限檢查：檔案擁有者 或 ADMIN/MANAGER
    owner_id_for_crud = None # 預設情況下，ADMIN/MANAGER 可以修改任何檔案
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        if file_to_rename.owner_id != current_user.id:
            logger.warning(f"User {current_user.username} (Role: {current_user.role}) not authorized to rename file ID: {file_id} owned by {file_to_rename.owner_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to rename this file")
        owner_id_for_crud = current_user.id # 普通使用者，傳遞 owner_id 以確保只修改自己的

    updated_file = crud_file.update_file_filename(
        db=db,
        file_id=file_id,
        new_filename=file_rename_data.new_filename,
        owner_id=owner_id_for_crud # 如果是 ADMIN/MANAGER，owner_id_for_crud 會是 None
    )

    if not updated_file:
        # 這種情況理論上不應該發生，因為上面已經檢查過檔案存在且權限符合
        # 但如果 update_file_filename 內部因為某些原因 (例如 owner_id 不匹配且不是 ADMIN) 返回 None
        logger.error(f"Failed to update filename for file ID: {file_id} by user {current_user.username}, possibly due to ownership mismatch in CRUD despite role.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not rename file, unexpected issue.") # 或者更具體的錯誤

    logger.info(f"File ID: {file_id} successfully renamed to '{updated_file.filename}' by user {current_user.username}")
    return updated_file

@router.get("/all", response_model=List[FileRead], dependencies=[Depends(require_manager_or_admin_role)])
async def list_all_files_for_admin(
    db: Session = Depends(get_db),
    username: Optional[str] = Query(None, description="Filter files by owner's username"),
    email: Optional[str] = Query(None, description="Filter files by owner's email"),
    skip: int = 0,
    limit: int = 100
):
    """
    (Admin/Manager Only) 獲取系統中的所有檔案，可按使用者名稱或 email 過濾。
    """
    owner_id: Optional[int] = None
    if username:
        user = crud_user.get_user_by_username(db, username=username)
        if not user:
            return [] # 如果找不到使用者，直接回傳空列表
        owner_id = user.id
    elif email:
        user = crud_user.get_user_by_email(db, email=email)
        if not user:
            return []
        owner_id = user.id
        
    files = crud_file.get_all_files(db=db, owner_id=owner_id, skip=skip, limit=limit)
    return files