# backend/app/dependencies.py
from functools import lru_cache
from fastapi import HTTPException, status

from app.services.storage_interface import StorageInterface
from app.services.s3_service import S3Service
from app.services.gcs_service import GCSService  # Import GCSService if needed
from app.core.config import settings


# 使用 @lru_cache(maxsize=None) 確保 service 只會被初始化一次
# 這是一個高效的單例模式實現
@lru_cache(maxsize=None)
def get_storage_service() -> StorageInterface:
    """
    Storage Service Factory.
    Reads the STORAGE_PROVIDER from settings and returns the corresponding
    storage service instance. Caches the instance for performance.
    
    Raises:
        HTTPException: If the storage service cannot be initialized due to
                       configuration errors or other issues.
        ValueError: If the configured STORAGE_PROVIDER is unsupported.
    """
    provider = settings.STORAGE_PROVIDER.lower()
    
    try:
        # 根據 provider 決定要實體化哪個服務
        if provider == "s3":
            print("Initializing S3Service...")
            service = S3Service()
        elif provider == "gcs":
            print("Initializing GCSService...")
            service = GCSService()
        else:
            # 如果設定了不支援的 provider，直接拋出錯誤
            raise ValueError(f"Unsupported storage provider: '{provider}'")
            
        return service

    except (ValueError, ConnectionError) as e:
        # 捕捉由 S3Service 或 GCSService 的 __init__ 拋出的設定錯誤或連線錯誤
        # 並將其轉換為 HTTP 503 錯誤，告知客戶端服務暫時不可用
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Storage service ('{provider}') could not be initialized: {e}"
        )
    except Exception as e:
        # 捕捉其他未預期的初始化錯誤
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An unexpected error occurred while initializing the storage service: {e}"
        )

# 您原本的 FastAPI 相依性注入函式可以簡化成這樣
# 這個函式可以直接在 FastAPI 的 depends() 中使用
def get_storage_dependency() -> StorageInterface:
    return get_storage_service()