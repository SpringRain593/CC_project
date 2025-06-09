from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie # 新增 Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.crud import user as crud_user
from app.crud import refresh_token as crud_refresh_token # 新增匯入
from app.core.security import create_access_token, get_current_active_user
from app.db.session import get_db
from app.core.config import settings #
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    db_user_by_email = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    db_user_by_username = crud_user.get_user_by_username(db, username=user_in.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    created_user = crud_user.create_user(db=db, user=user_in)
    return created_user


@router.post("/login/access-token"
            # , response_model=Token # 我們將直接回傳 Response 物件來設定 cookie，所以這裡可以先註解掉或移除
            )
async def login_for_access_token(
    response: Response, # 注入 Response 物件以設定 cookie
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud_user.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 產生 Access Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) #
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 產生並儲存 Refresh Token
    refresh_token_expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    # 產生一個唯一的 refresh token 字串，可以考慮將其也存入 refresh_token 表中
    # 或者直接使用 crud_refresh_token.create_refresh_token 內部產生的 token
    
    # 我們讓 create_refresh_token 內部產生 token value
    db_refresh_token = crud_refresh_token.create_refresh_token(
        db=db, user=user, expires_delta=refresh_token_expires_delta
    )

    # 設定 Refresh Token 到 HttpOnly Cookie
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=db_refresh_token.token, # 使用儲存到資料庫的 token 值
        httponly=settings.REFRESH_TOKEN_COOKIE_HTTPONLY,
        secure=settings.REFRESH_TOKEN_COOKIE_SECURE, # 在生產中應為 True
        samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
        path=settings.REFRESH_TOKEN_COOKIE_PATH,
        domain=settings.REFRESH_TOKEN_COOKIE_DOMAIN,
        max_age=int(refresh_token_expires_delta.total_seconds()) # Cookie 的 max_age 以秒為單位
    )
    
    # 回傳 Access Token 在 JSON body 中
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@router.post("/refresh-token")
async def refresh_access_token(
    response: Response, # 用於設定新的 refresh token cookie
    # 從 cookie 中提取 refresh token，如果 cookie 不存在，refresh_token_value 會是 None
    refresh_token_value: Optional[str] = Cookie(None, alias=settings.REFRESH_TOKEN_COOKIE_NAME),
    db: Session = Depends(get_db)
):
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookie",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. 驗證舊的 Refresh Token
    old_refresh_token_obj = crud_refresh_token.get_active_refresh_token_by_value(
        db, token_value=refresh_token_value
    )

    if not old_refresh_token_obj:
        # 如果 token 無效或已過期/已撤銷，則要求重新登入
        # 為了安全，可以選擇同時撤銷該使用者所有可能的 refresh token (如果能追溯到使用者)
        # 但這裡我們先簡單處理：拒絕並要求重新登入
        response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME, path=settings.REFRESH_TOKEN_COOKIE_PATH, domain=settings.REFRESH_TOKEN_COOKIE_DOMAIN)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. (重要) 撤銷舊的 Refresh Token (使其只能使用一次)
    crud_refresh_token.revoke_refresh_token(db, token=old_refresh_token_obj)
    
    # 3. 獲取使用者資訊
    user = old_refresh_token_obj.user 
    if not user or not user.is_active:
        response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME, path=settings.REFRESH_TOKEN_COOKIE_PATH, domain=settings.REFRESH_TOKEN_COOKIE_DOMAIN)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. 產生新的 Access Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) #
    new_access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 5. 產生並儲存新的 Refresh Token (滾動機制)
    new_refresh_token_expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_db_refresh_token = crud_refresh_token.create_refresh_token(
        db=db, user=user, expires_delta=new_refresh_token_expires_delta
    )

    # 6. 設定新的 Refresh Token到 HttpOnly Cookie
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=new_db_refresh_token.token,
        httponly=settings.REFRESH_TOKEN_COOKIE_HTTPONLY,
        secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
        samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
        path=settings.REFRESH_TOKEN_COOKIE_PATH,
        domain=settings.REFRESH_TOKEN_COOKIE_DOMAIN,
        max_age=int(new_refresh_token_expires_delta.total_seconds())
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


# ... (繼續在 auth.py 中) ...

@router.post("/logout")
async def logout(
    response: Response,
    # 我們需要知道是哪個 refresh token 需要被撤銷
    # 通常是從 cookie 來的那個
    refresh_token_value: Optional[str] = Cookie(None, alias=settings.REFRESH_TOKEN_COOKIE_NAME),
    db: Session = Depends(get_db),
    # 也可以選擇依賴 get_current_user 來確保只有登入使用者可以登出，
    # 但如果 refresh token 本身就能識別使用者，則可能不是嚴格必要。
    # current_user: User = Depends(get_current_user) # 可選
):
    if refresh_token_value:
        token_obj = crud_refresh_token.get_active_refresh_token_by_value(db, token_value=refresh_token_value)
        if token_obj:
            crud_refresh_token.revoke_refresh_token(db, token=token_obj)
            # 或者，如果想撤銷該使用者的所有 refresh token：
            # crud_refresh_token.revoke_all_refresh_tokens_for_user(db, user_id=token_obj.user_id)
    
    # 清除用戶端的 refresh token cookie
    response.delete_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME, 
        path=settings.REFRESH_TOKEN_COOKIE_PATH, 
        domain=settings.REFRESH_TOKEN_COOKIE_DOMAIN
    )
    return {"message": "Successfully logged out"}