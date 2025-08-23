# app/db/models/role.py
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from app.db.models.base import Base, TimestampMixin, OperatorMixin

class RoleModel(Base, TimestampMixin, OperatorMixin):
    """角色模型"""
    __tablename__ = 't_sys_role'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键')
    code = Column(String(50), comment='角色编码')
    name = Column(String(50), comment='角色名称')
    org_id = Column(BigInteger, comment='组织id')
    
    # 关联关系
    users = relationship("UserModel", secondary="t_sys_user_role", back_populates="roles")
    permissions = relationship("FunctionPermissionModel", 
                             secondary="t_sys_role_func_per",
                             back_populates="roles")

class UserRoleModel(Base):
    """用户角色关联模型"""
    __tablename__ = 't_sys_user_role'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键')
    user_id = Column(BigInteger, ForeignKey('t_sys_user.id'), comment='用户id')
    role_id = Column(BigInteger, ForeignKey('t_sys_role.id'), comment='角色id')

class FunctionPermissionModel(Base, TimestampMixin, OperatorMixin):
    """功能权限模型"""
    __tablename__ = 't_sys_function_permission'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键')
    type = Column(String(1), comment='类型 1：目录 2：菜单 3：按钮')
    value = Column(String(255), comment='权限码')
    parent_id = Column(BigInteger, comment='父级菜单')
    title = Column(String(255), comment='菜单名称')
    component = Column(String(255), comment='组件路径')
    name = Column(String(255), comment='组件名称')
    icon = Column(String(255), comment='图标')
    path = Column(String(255), comment='路径')
    redirect = Column(String(255), comment='重定向路径')
    active_menu = Column(String(255), comment='高亮菜单')
    hidden = Column(Boolean, default=False, comment='是否隐藏')
    always_show = Column(Boolean, default=True, comment='是否一直显示')
    no_cache = Column(Boolean, default=False, comment='是否清空缓存')
    breadcrumb = Column(Boolean, default=True, comment='是否显示面包屑')
    affix = Column(Boolean, default=False, comment='是否固定在标签页')
    no_tags_view = Column(Boolean, default=False, comment='是否隐藏标签页')
    order_num = Column(Integer, comment='排序')
    can_to = Column(Boolean, default=True, comment='是否可跳转')
    status = Column(Boolean, default=True, comment='状态')
    
    # 关联关系
    roles = relationship("RoleModel", secondary="t_sys_role_func_per", back_populates="permissions")

class RoleFunctionPermissionModel(Base):
    """角色功能权限关联模型"""
    __tablename__ = 't_sys_role_func_per'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键')
    role_id = Column(BigInteger, ForeignKey('t_sys_role.id'), comment='角色id')
    func_per_id = Column(BigInteger, ForeignKey('t_sys_function_permission.id'), comment='功能权限id')