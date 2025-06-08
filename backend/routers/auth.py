from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging

from models import get_user_by_name, create_user
from utils.security import hash_password, verify_password, create_jwt

router = APIRouter(prefix="/api", tags=["auth"])
log = logging.getLogger("cloudfs.auth")

class UserIn(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserIn):
    if get_user_by_name(data.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    uid = create_user(data.username, hash_password(data.password))
    log.info(f"register-success username={data.username} uid={uid}")
    return {"message": "registered"}

@router.post("/login")
def login(data: UserIn):
    user = get_user_by_name(data.username)
    if not user or not verify_password(data.password, user["pw_hash"]):
        log.warning(f"login-fail username={data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt({
        "sub": str(user["user_id"]),      # 這行改成 str
        "name": user["username"],
        "role": user["role"]
    })

    log.info(f"login-success username={data.username}")
    return {"access_token": token, "token_type": "bearer"}

