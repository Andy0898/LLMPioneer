from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.db.models.user import UserModel
from app.db.models.role import RoleModel, FunctionPermissionModel, RoleFunctionPermissionModel, UserRoleModel
from app.services.role import RoleService, FunctionPermissionService

async def init_admin(db: AsyncSession):
    """初始化超级管理员用户和权限"""
    
    # 1. 创建超级管理员角色
    admin_role = RoleModel(
        code="super_admin",
        name="超级管理员",
        create_by="system"
    )
    db.add(admin_role)
    await db.flush()
    
    # 2. 创建基础权限
    permissions = [
        {"id": 1, "type": "2", "parent_id": 0, "value": "SystemManagement", "title": "系统管理", "component": ""},
        # 用户管理权限
        {"id": 2, "type": "2", "parent_id": 1, "value": "user:list", "title": "用户管理", "component": "user/index"},
        {"id": 3, "type": "3", "value": "user:create", "title": "创建用户"},
        {"id": 4, "type": "3", "value": "user:update", "title": "更新用户"},
        {"id": 5, "type": "3", "value": "user:delete", "title": "删除用户"},
        {"id": 6, "type": "3", "value": "user:read", "title": "查看用户"},
        
        # 角色管理权限
        {"id": 7, "type": "2", "parent_id": 1, "value": "role:list", "title": "角色列表", "component": "role/index"},
        {"id": 8, "type": "3", "value": "role:create", "title": "创建角色"},
        {"id": 9, "type": "3", "value": "role:update", "title": "更新角色"},
        {"id": 10, "type": "3", "value": "role:delete", "title": "删除角色"},
        {"id": 11, "type": "3", "value": "role:read", "title": "查看角色"},
        
        # 权限管理权限
        {"id": 12, "type": "2", "parent_id": 1, "value": "permission:list", "title": "权限列表", "component": "permission/index"},
        {"id": 13, "type": "3", "value": "permission:create", "title": "创建权限"},
        {"id": 14, "type": "3", "value": "permission:update", "title": "更新权限"},
        {"id": 15, "type": "3", "value": "permission:delete", "title": "删除权限"},
        {"id": 16, "type": "3", "value": "permission:read", "title": "查看权限"},
        {"id": 17, "type": "3", "value": "permission:assign", "title": "分配权限"},
    ]
    
    db_permissions = []
    for perm in permissions:
        db_perm = FunctionPermissionModel(**perm, create_by="system")
        db.add(db_perm)
        db_permissions.append(db_perm)
    await db.flush()
    
    # 3. 为超级管理员角色分配所有权限
    for perm in db_permissions:
        db.add(RoleFunctionPermissionModel(
            role_id=admin_role.id,
            func_per_id=perm.id
        ))
    
    # 4. 创建admin用户
    admin_user = UserModel(
        user_name="admin",
        password=get_password_hash("admin123"),  # 默认密码
        user_type="0",  # 超级管理员类型
        status=True,
        create_by="system"
    )
    db.add(admin_user)
    await db.flush()
    
    # 5. 为admin用户分配超级管理员角色
    db.add(UserRoleModel(
        user_id=admin_user.id,
        role_id=admin_role.id
    ))
    
    await db.commit()
    
    return {
        "admin_user": admin_user,
        "admin_role": admin_role,
        "permissions": db_permissions
    } 