from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from utils.file_ops import save_upload, open_as_bytes
from models import insert_file, get_file  # 確保有實作
from auth import current_user
import os, logging

log = logging.getLogger("cloudfs")
router = APIRouter(prefix="/api", tags=["files"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(current_user)
):
    path = save_upload(user["name"], file)
    size = os.path.getsize(path)
    fid = insert_file(user["sub"], path, file.filename, size)
    log.info(f"upload uid={user['sub']} path={path}")
    return {"file_id": fid, "filename": file.filename, "size": size}

@router.get("/download/{file_id}")
def download_file(file_id: int, user=Depends(current_user)):
    rec = get_file(file_id, user["sub"])
    if not rec:
        raise HTTPException(404, "Not found")
    data = open_as_bytes(rec["file_path"])
    return StreamingResponse(
        iter([data]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{rec["filename"]}"'}
    )


