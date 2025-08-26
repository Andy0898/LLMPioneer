# app/services/permission_manager.py
from typing import List, Dict, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.role_service import RoleService
from app.db.models import RoleModel, FunctionPermissionModel

class PermissionManager:
    """
    权限管理器 - 统一管理用户权限相关的操作
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_service = RoleService(db)
    
    async def get_user_permission_info(self, user_id: int) -> Dict:
        """
        获取用户的完整权限信息
        """
        user_roles = await self.role_service.get_user_roles(user_id)
        is_super_admin = self._is_super_admin(user_roles)
        
        if is_super_admin:
            return {
                "is_super_admin": True,
                "can_access_all": True,
                "roles": [{"code": role.code, "name": role.name} for role in user_roles],
                "permissions": ["*"],
                "permission_level": "super_admin"
            }
        
        # 获取具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        
        return {
            "is_super_admin": False,
            "can_access_all": False,
            "roles": [{"code": role.code, "name": role.name} for role in user_roles],
            "permissions": list(user_permissions),
            "permission_level": "normal_user"
        }
    
    async def check_permission(self, user_id: int, required_permission: str) -> bool:
        """
        检查用户是否有指定权限
        """
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员拥有所有权限
        if self._is_super_admin(user_roles):
            return True
        
        # 检查具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        return required_permission in user_permissions
    
    async def check_permissions(self, user_id: int, required_permissions: List[str]) -> Dict[str, bool]:
        """
        检查用户是否有指定的多个权限
        返回每个权限的检查结果
        """
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员拥有所有权限
        if self._is_super_admin(user_roles):
            return {perm: True for perm in required_permissions}
        
        # 检查具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        return {perm: perm in user_permissions for perm in required_permissions}
    
    async def check_any_permission(self, user_id: int, required_permissions: List[str]) -> bool:
        """
        检查用户是否有指定权限中的任意一个
        """
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员拥有所有权限
        if self._is_super_admin(user_roles):
            return True
        
        # 检查具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        return any(perm in user_permissions for perm in required_permissions)
    
    async def check_all_permissions(self, user_id: int, required_permissions: List[str]) -> bool:
        """
        检查用户是否有指定的所有权限
        """
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员拥有所有权限
        if self._is_super_admin(user_roles):
            return True
        
        # 检查具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        return all(perm in user_permissions for perm in required_permissions)
    
    async def get_user_accessible_resources(self, user_id: int, resource_type: str = None) -> List[str]:
        """
        获取用户可访问的资源列表
        """
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员可以访问所有资源
        if self._is_super_admin(user_roles):
            return ["*"]
        
        # 获取具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        
        if resource_type:
            # 过滤特定类型的资源权限
            return [perm for perm in user_permissions if perm.startswith(f"{resource_type}:")]
        
        return list(user_permissions)
    
    async def validate_data_access(
        self, 
        user_id: int, 
        resource_owner_id: int, 
        resource_org_id: int = None,
        user_org_id: int = None
    ) -> bool:
        """
        验证数据访问权限
        """
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员可以访问所有数据
        if self._is_super_admin(user_roles):
            return True
        
        # 用户可以访问自己的数据
        if user_id == resource_owner_id:
            return True
        
        # 用户可以访问同组织的数据
        if resource_org_id and user_org_id and resource_org_id == user_org_id:
            return True
        
        return False
    
    def _is_super_admin(self, user_roles: List[RoleModel]) -> bool:
        """
        检查用户是否是超级管理员
        """
        return any(role.code == "super_admin" for role in user_roles)
    
    async def _get_user_permissions(self, user_roles: List[RoleModel]) -> Set[str]:
        """
        获取用户的所有权限
        """
        user_permissions = set()
        for role in user_roles:
            role_permissions = await self.role_service.get_role_permissions(role.id)
            user_permissions.update(perm.value for perm in role_permissions)
        return user_permissions
    
    async def get_permission_summary(self, user_id: int) -> Dict:
        """
        获取用户权限摘要信息
        """
        permission_info = await self.get_user_permission_info(user_id)
        
        return {
            "user_id": user_id,
            "is_super_admin": permission_info["is_super_admin"],
            "can_access_all": permission_info["can_access_all"],
            "total_permissions": len(permission_info["permissions"]) if not permission_info["is_super_admin"] else "unlimited",
            "roles_count": len(permission_info["roles"]),
            "permission_level": permission_info["permission_level"]
        }
