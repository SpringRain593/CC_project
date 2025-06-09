# backend/app/services/gcs_service.py
import os
from google.cloud import storage
from google.api_core.exceptions import GoogleAPICallError
from typing import IO, Optional, Any
import logging
from urllib.parse import quote
import datetime

from app.core.config import settings
from .storage_interface import StorageInterface

logger = logging.getLogger(__name__)

class GCSService(StorageInterface):
    def __init__(self):
        try:
            if not settings.GOOGLE_APPLICATION_CREDENTIALS or not settings.GCS_BUCKET_NAME:
                raise ValueError("GCS credentials or bucket name are not configured.")

            # Google Cloud client library會自動使用 GOOGLE_APPLICATION_CREDENTIALS 環境變數
            self.storage_client = storage.Client()
            self.bucket_name = settings.GCS_BUCKET_NAME
            self.bucket = self.storage_client.bucket(self.bucket_name)
            logger.info(f"Successfully connected to GCS bucket: {self.bucket_name}")

        except FileNotFoundError:
            logger.error(f"GCS credentials file not found at: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
            raise
        except Exception as e:
            logger.error(f"Error initializing GCSService: {e}")
            raise

    def upload_file(
        self, file_content: IO[Any], destination_path: str, content_type: Optional[str] = None
    ) -> str:
        """上傳檔案到 GCS. GCS 中的物件稱為 'blob'."""
        try:
            # GCS 中的物件被稱為 Blob (二進位大型物件)
            blob = self.bucket.blob(destination_path)
            
            # 將檔案指標移至開頭，確保能完整讀取
            file_content.seek(0)
            
            blob.upload_from_file(file_content, content_type=content_type)
            logger.info(f"Successfully uploaded to GCS: {self.bucket_name}/{destination_path}")
            return destination_path
        except GoogleAPICallError as e:
            logger.error(f"Failed to upload to GCS ({self.bucket_name}/{destination_path}): {e}")
            raise IOError(f"GCS upload failed: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during GCS upload: {e}")
            raise

    def delete_file(self, storage_path: str) -> None:
        """從 GCS 刪除檔案."""
        try:
            blob = self.bucket.blob(storage_path)
            blob.delete()
            logger.info(f"Successfully deleted from GCS: {self.bucket_name}/{storage_path}")
        except GoogleAPICallError as e:
            logger.error(f"Failed to delete {storage_path} from GCS: {e}")
            raise IOError(f"GCS delete failed: {e}")

    def generate_presigned_url(
        self, storage_path: str,
        expiration_seconds: int,
        http_method: str = "GET",
        download_filename: Optional[str] = None
    ) -> Optional[str]:
        """產生 GCS 的預先簽署 URL."""
        if http_method.upper() not in ["GET", "PUT", "POST", "DELETE"]:
            logger.error(f"Unsupported http_method '{http_method}' for GCS signed URL.")
            return None
        
        try:
            blob = self.bucket.blob(storage_path)
            
            disposition = None
            if http_method.upper() == "GET" and download_filename:
                try:
                    download_filename.encode('ascii')
                    disposition = f'attachment; filename="{download_filename}"'
                except UnicodeEncodeError:
                    encoded_filename = quote(download_filename)
                    disposition = f"attachment; filename*=UTF-8''{encoded_filename}"

            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(seconds=expiration_seconds),
                method=http_method.upper(),
                response_disposition=disposition, # 用於下載時的檔名
            )
            return url
        except GoogleAPICallError as e:
            logger.error(f"Failed to generate GCS signed URL for {storage_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred generating signed URL: {e}")
            return None