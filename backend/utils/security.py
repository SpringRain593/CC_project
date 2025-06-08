from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import bcrypt
from config import settings

ALG = "HS256"
TOKEN_TTL = 7  # days

def hash_password(pwd: str) -> str:
    return bcrypt.hash(pwd)

def verify_password(pwd: str, pw_hash: str) -> bool:
    return bcrypt.verify(pwd, pw_hash)

def create_jwt(data: dict) -> str:
    to_encode = data.copy()

    # ★ 只要確定 sub 是 str
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    to_encode["exp"] = datetime.utcnow() + timedelta(days=TOKEN_TTL)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALG)

def decode_jwt(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALG])

print(f"Loaded SECRET_KEY = {settings.SECRET_KEY}")
