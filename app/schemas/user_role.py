from typing import Optional
from pydantic import BaseModel

class UserRoleBase(BaseModel):
    """用户角色关联基础模型"""
    user_id: Optional[int] = None
    role_id: Optional[int] = None

class UserRoleCreate(UserRoleBase):
    """用户角色关联创建模型"""
    user_id: int
    role_id: int

class UserRoleUpdate(UserRoleBase):
    """用户角色关联更新模型"""
    pass

class UserRole(UserRoleBase):
    """用户角色关联响应模型"""
    id: int

    class Config:
        from_attributes = True 