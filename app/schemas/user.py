from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from .role import Role

# 用户基础模型
class UserBase(BaseModel):
    user_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[int] = None
    user_type: str = "1"
    status: Optional[bool] = True
    avatar: Optional[str] = None
    remark: Optional[str] = None

# 创建用户请求模型
class UserCreate(UserBase):
    user_name: str
    password: str
    role_ids: Optional[List[int]] = []

# 更新用户请求模型
class UserUpdate(UserBase):
    password: Optional[str] = None
    role_ids: Optional[List[int]] = []

# 用户登录请求模型
class UserLogin(BaseModel):
    user_name: str
    password: str

# 修改密码请求模型
class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

# 用户响应模型
class User(UserBase):
    id: int
    is_locked: bool = False
    error_num: int = 0
    last_login_time: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None
    roles: List[Role] = []

    class Config:
        from_attributes = True
        populate_by_name = True

# Token响应模型
class Token(BaseModel):
    access_token: str
    token_type: str
    roles: List[dict] = []
    permissions: List[str] = []

# Token数据模型
class TokenData(BaseModel):
    user_name: str
    user_id: int 