# backend/app/services/s3_service.py
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import IO, Optional, Any
import logging
from urllib.parse import quote
from app.core.config import settings
from .storage_interface import StorageInterface

logger = logging.getLogger(__name__)

class S3Service(StorageInterface):
    def __init__(self):
        try:
            # 建立一個字典來動態組織要傳給 boto3 client 的參數
            client_kwargs = {
                "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
                "region_name": settings.AWS_REGION,
            }


  
            logger.info("Using AWS Session Token.")
            client_kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN


            self.s3_client = boto3.client("s3", **client_kwargs)
            
            self.bucket_name = settings.S3_BUCKET_NAME
            if not self.bucket_name:
                raise ValueError("S3_BUCKET_NAME is not configured.")
       
        except NoCredentialsError:
            logger.error("AWS/MinIO credentials not found. Ensure they are configured in your .env file.")
            raise
        except Exception as e:
            logger.error(f"Error initializing S3Service: {e}")
            raise

    def upload_file(
        self, file_content: IO[Any], destination_path: str, content_type: Optional[str] = None
    ) -> str:
        if settings.MINIO_ENDPOINT_URL:
            extra_args = {}
        else:
            extra_args = {"ServerSideEncryption": "AES256"}
        if content_type:
            extra_args["ContentType"] = content_type
        
        if not self.s3_client or not self.bucket_name:
            logger.error("S3 client or bucket name not initialized properly.")
            raise ConnectionError("S3 client not initialized.")

        try:
            self.s3_client.upload_fileobj(
                file_content,
                self.bucket_name,
                destination_path,
                ExtraArgs=extra_args
            )
            logger.info(f"Successfully uploaded to S3: {self.bucket_name}/{destination_path}")
            return destination_path
        except ClientError as e:
            logger.error(f"Failed to upload to S3 ({self.bucket_name}/{destination_path}): {e}")
            raise IOError(f"S3 upload failed: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during S3 upload: {e}")
            raise

    def delete_file(self, storage_path: str) -> None:
        if not self.s3_client or not self.bucket_name:
            logger.error("S3 client or bucket name not initialized properly.")
            raise ConnectionError("S3 client not initialized.")
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=storage_path)
            logger.info(f"Successfully deleted from S3: {self.bucket_name}/{storage_path}")
        except ClientError as e:
            logger.error(f"Failed to delete {storage_path} from S3: {e}")
            raise IOError(f"S3 delete failed: {e}")

    def generate_presigned_url(
        self, storage_path: str,
        expiration_seconds: int,
        http_method: str = "GET",
        download_filename: Optional[str] = None
    ) -> Optional[str]:
        if not self.s3_client or not self.bucket_name:
            logger.error("S3 client or bucket name not initialized properly.")
            return None 

        client_method_map = {
            "GET": "get_object",
            "PUT": "put_object",
        }
        s3_client_method = client_method_map.get(http_method.upper())

        if not s3_client_method:
            logger.error(f"Unsupported http_method '{http_method}' for S3 presigned URL generation.")
            return None

        params = {"Bucket": self.bucket_name, "Key": storage_path}
        
        if http_method.upper() == "GET" and download_filename:
            try:
                # 先嘗試將檔名編碼為 ASCII，如果失敗，則表示包含非 ASCII 字元
                download_filename.encode('ascii')
                # 如果成功，表示是純 ASCII 檔名，使用簡單格式
                disposition = f'attachment; filename="{download_filename}"'
            except UnicodeEncodeError:
                # 如果失敗，表示包含中文等字元，使用 RFC 6266 推薦的格式
                encoded_filename = quote(download_filename)
                disposition = f"attachment; filename*=UTF-8''{encoded_filename}"

            params["ResponseContentDisposition"] = disposition
        
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod=s3_client_method,
                Params=params,
                ExpiresIn=expiration_seconds,
                HttpMethod=http_method.upper()
            )
            
            if settings.MINIO_ENDPOINT_URL and settings.MINIO_SERVER_URL:
                # 如果是 MinIO，則需要將 URL 的域名部分替換為 MinIO 的服務器 URL
                url = url.replace(settings.MINIO_ENDPOINT_URL, settings.MINIO_SERVER_URL)
            
            return url
        except ClientError as e:
            logger.error(f"Failed to generate S3 presigned URL for {storage_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred generating presigned URL: {e}")
            return None