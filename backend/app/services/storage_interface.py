# backend/app/services/storage_interface.py
from abc import ABC, abstractmethod
from typing import IO, Optional, Any # IO for file-like objects, Any for file_content

class StorageInterface(ABC):
    @abstractmethod
    def upload_file(
        self, file_content: IO[Any], destination_path: str, content_type: Optional[str] = None
    ) -> str: # Returns the final storage path or key
        pass

    @abstractmethod
    def delete_file(self, storage_path: str) -> None:
        pass

    @abstractmethod
    def generate_presigned_url(
        self,
        storage_path: str,
        expiration_seconds: int,
        http_method: str = "GET",
        download_filename: Optional[str] = None
    ) -> Optional[str]:
        pass

    # Add other methods as needed, e.g., download_file_obj, list_files