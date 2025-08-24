# app/db/models/user.py
from __future__ import annotations
from typing import TYPE_CHECKING, List, Union, Optional
from sqlalchemy import Column, String, Boolean, Integer, Table, ForeignKey, BigInteger, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.associationproxy import association_proxy
from app.db.models.base import Base, TimestampMixin, OperatorMixin
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .role import RoleModel
    from .conversation import ConversationModel # NEW IMPORT for type hinting

# 1. 先定义主模型（被引用的模型）
class UserModel(Base, TimestampMixin, OperatorMixin):
    __tablename__ = 't_sys_user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment='主键')
    user_type: Mapped[str] = mapped_column(String(1), default='1', comment='用户类型。1-普通用户')
    user_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, comment='用户名')
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment='密码')
    phone: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment='手机号')
    gender: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment='性别')
    error_num: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='错误登录次数')
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment='是否被锁定：0未锁定；1：已锁定')
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment='状态0：禁用；1：启用')
    
    # 关系定义
    user_roles: Mapped[List["UserRoleModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    roles: Mapped[List["RoleModel"]] = association_proxy("user_roles", "role")
    conversations: Mapped[List["ConversationModel"]] = relationship(back_populates="user") # Corrected relationship

    __table_args__ = {'extend_existing': True}

# 2. 最后定义关联模型（引用其他模型的模型）
class UserRoleModel(Base, TimestampMixin, OperatorMixin):
    """用户角色关联模型"""
    __tablename__ = 't_sys_user_role'
    
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('t_sys_user.id'), primary_key=True, comment='用户ID')
    role_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('t_sys_role.id'), primary_key=True, comment='角色ID')
    
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), comment='分配时间')
    assigned_by: Mapped[str] = mapped_column(String(100), comment='分配人')
    
    # 关系定义
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="user_roles")
    role: Mapped["RoleModel"] = relationship("RoleModel", back_populates="user_roles")

    __table_args__ = {'extend_existing': True}