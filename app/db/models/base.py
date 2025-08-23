from datetime import datetime, timezone
from typing import Any
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, String

class Base(DeclarativeBase):
    """
    基础模型类，所有模型都应该继承这个类
    """
    id: Any
    __name__: str
    
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
    create_time = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), comment='创建时间')
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now(timezone.utc), comment='更新时间')

class OperatorMixin:
    """
    操作者Mixin，包含创建人和更新人
    """
    create_by = Column(String(100), nullable=False, comment='创建人')
    update_by = Column(String(100), nullable=True, comment='更新人') 