from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String
from sqlalchemy.orm import declared_attr

class Base(DeclarativeBase):
    """
    基础模型类，所有模型都应该继承这个类
    """
    # 移除 id 字段，让子类自己定义
    # 移除 __name__ 字段，这不是数据库字段
    
    # 生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        """
        将类名转换为表名，例如：UserModel -> user
        移除Model后缀，并转换为小写
        """
        if cls.__name__.endswith('Model'):
            return cls.__name__[:-5].lower()
        return cls.__name__.lower()

class TimestampMixin:
    """
    时间戳Mixin，包含创建时间和更新时间
    """
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), comment='创建时间')
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc), comment='更新时间')

class OperatorMixin:
    """
    操作者Mixin，包含创建人和更新人
    """
    create_by: Mapped[str] = mapped_column(String(100), nullable=False, comment='创建人')
    update_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment='更新人')