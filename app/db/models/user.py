# app/db/models/user.py
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from app.db.models.base import Base, TimestampMixin, OperatorMixin

class UserModel(Base, TimestampMixin, OperatorMixin):
    """
    用户模型
    """
    __tablename__ = 't_sys_user'  # 使用实际的表名
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    user_type = Column(String(1), default='1', comment='用户类型。1-普通用户')
    user_name = Column(String(255), nullable=False, unique=True, comment='用户名')
    password = Column(String(255), nullable=True, comment='密码')
    phone = Column(String(255), nullable=True, comment='手机号')
    gender = Column(Integer, nullable=True, comment='性别')
    error_num = Column(Integer, nullable=False, default=0, comment='错误登录次数')
    is_locked = Column(Boolean, nullable=False, default=False, comment='是否被锁定：0未锁定；1：已锁定')
    status = Column(Boolean, nullable=False, default=True, comment='状态0：禁用；1：启用') 
    # 关联关系
    roles = relationship("RoleModel", secondary="t_sys_user_role", back_populates="users")