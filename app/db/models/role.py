# app/db/models/role.py
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.associationproxy import association_proxy
from app.db.models.base import Base, TimestampMixin, OperatorMixin
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .user import UserModel, UserRoleModel

# 1. 先定义主模型（被引用的模型）
class RoleModel(Base, TimestampMixin, OperatorMixin):
    __tablename__ = 't_sys_role'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment='主键')
    code: Mapped[Optional[str]] = mapped_column(String(50), comment='角色编码')
    name: Mapped[Optional[str]] = mapped_column(String(50), comment='角色名称')
    org_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment='组织id')
    
    # 关系定义
    user_roles: Mapped[List["UserRoleModel"]] = relationship(back_populates="role")
    role_permissions: Mapped[List["RolePermissionModel"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    permissions: Mapped[List["FunctionPermissionModel"]] = association_proxy("role_permissions", "permission")
    
    __table_args__ = {'extend_existing': True}

class FunctionPermissionModel(Base, TimestampMixin, OperatorMixin):
    __tablename__ = 't_sys_function_permission'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment='主键')
    type: Mapped[Optional[str]] = mapped_column(String(1), comment='类型 1：目录 2：菜单 3：按钮')
    value: Mapped[Optional[str]] = mapped_column(String(255), comment='权限码')
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment='父级菜单')
    title: Mapped[Optional[str]] = mapped_column(String(255), comment='菜单名称')
    component: Mapped[Optional[str]] = mapped_column(String(255), comment='组件路径')
    name: Mapped[Optional[str]] = mapped_column(String(255), comment='组件名称')
    icon: Mapped[Optional[str]] = mapped_column(String(255), comment='图标')
    path: Mapped[Optional[str]] = mapped_column(String(255), comment='路径')
    redirect: Mapped[Optional[str]] = mapped_column(String(255), comment='重定向路径')
    active_menu: Mapped[Optional[str]] = mapped_column(String(255), comment='高亮菜单')
    hidden: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否隐藏')
    always_show: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否一直显示')
    no_cache: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否清空缓存')
    breadcrumb: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否显示面包屑')
    affix: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否固定在标签页')
    no_tags_view: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否隐藏标签页')
    order_num: Mapped[Optional[int]] = mapped_column(Integer, comment='排序')
    can_to: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否可跳转')
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment='状态')
    
    # 关系定义
    role_permissions: Mapped[List["RolePermissionModel"]] = relationship(back_populates="permission")
    roles: Mapped[List["RoleModel"]] = association_proxy("role_permissions", "role")
    
    __table_args__ = {'extend_existing': True}

# 2. 最后定义关联模型（引用其他模型的模型）
class RolePermissionModel(Base, TimestampMixin, OperatorMixin):
    """角色权限关联模型"""
    __tablename__ = 't_sys_role_func_per'
    
    role_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('t_sys_role.id'), primary_key=True, comment='角色ID')
    func_per_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('t_sys_function_permission.id'), primary_key=True, comment='权限ID')
    
    # 可以添加额外字段
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), comment='分配时间')
    assigned_by: Mapped[str] = mapped_column(String(100), comment='分配人')
    permission_level: Mapped[Optional[str]] = mapped_column(String(10), comment='权限级别：read, write, admin')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否激活')
    
    # 关系定义
    role: Mapped["RoleModel"] = relationship("RoleModel", back_populates="role_permissions")
    permission: Mapped["FunctionPermissionModel"] = relationship("FunctionPermissionModel", back_populates="role_permissions")
    
    __table_args__ = {'extend_existing': True}
