import os, uuid, shutil
from fastapi import UploadFile
from config import settings

BASE_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")  # fallback 避免空值

def save_upload(user_prefix: str, upfile: UploadFile) -> str:
    fname = f"{uuid.uuid4()}_{upfile.filename}"
    user_dir = os.path.join(BASE_DIR, user_prefix)
    os.makedirs(user_dir, exist_ok=True)
    dest = os.path.join(user_dir, fname)
    with open(dest, "wb") as f:
        shutil.copyfileobj(upfile.file, f)
    return dest

def open_as_bytes(filepath: str) -> bytes:
    with open(filepath, "rb") as f:
        return f.read()

