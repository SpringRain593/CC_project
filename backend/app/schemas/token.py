from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    # 如果您使用 user_id 作為 subject，可以是：
    # user_id: Optional[int] = None