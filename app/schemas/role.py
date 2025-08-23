from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class RoleBase(BaseModel):
    """角色基础模型"""
    code: Optional[str] = None
    name: Optional[str] = None
    org_id: Optional[int] = None

class RoleCreate(RoleBase):
    """角色创建模型"""
    code: str
    name: str

class RoleUpdate(RoleBase):
    """角色更新模型"""
    pass

class Role(RoleBase):
    """角色响应模型"""
    id: int
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class FunctionPermissionBase(BaseModel):
    """功能权限基础模型"""
    type: Optional[str] = None
    value: Optional[str] = None
    parent_id: Optional[int] = None
    title: Optional[str] = None
    component: Optional[str] = None
    name: Optional[str] = None
    icon: Optional[str] = None
    path: Optional[str] = None
    redirect: Optional[str] = None
    active_menu: Optional[str] = None
    hidden: Optional[bool] = False
    always_show: Optional[bool] = True
    no_cache: Optional[bool] = False
    breadcrumb: Optional[bool] = True
    affix: Optional[bool] = False
    no_tags_view: Optional[bool] = False
    order_num: Optional[int] = None
    can_to: Optional[bool] = True
    status: Optional[bool] = True

class FunctionPermissionCreate(FunctionPermissionBase):
    """功能权限创建模型"""
    type: str
    value: str
    title: str

class FunctionPermissionUpdate(FunctionPermissionBase):
    """功能权限更新模型"""
    pass

class FunctionPermission(FunctionPermissionBase):
    """功能权限响应模型"""
    id: int
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class RoleWithPermissions(Role):
    """带权限的角色响应模型"""
    permissions: List[FunctionPermission] = [] 