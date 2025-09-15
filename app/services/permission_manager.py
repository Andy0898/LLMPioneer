# app/services/permission_manager.py
from typing import List, Dict, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.role_service import RoleService
from app.db.models import RoleModel, FunctionPermissionModel
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

class PermissionManager:
    """
    权限管理器 - 统一管理用户权限相关的操作
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_service = RoleService(db)
        logger.info("PermissionManager initialized.")
    
    async def get_user_permission_info(self, user_id: int) -> Dict:
        """
        获取用户的完整权限信息
        """
        logger.info(f"Retrieving full permission info for user ID: {user_id}.")
        user_roles = await self.role_service.get_user_roles(user_id)
        is_super_admin = self._is_super_admin(user_roles)
        logger.debug(f"User {user_id} roles: {[role.code for role in user_roles]}, Is Super Admin: {is_super_admin}.")
        
        if is_super_admin:
            logger.info(f"User {user_id} is super admin, returning all permissions.")
            return {
                "is_super_admin": True,
                "can_access_all": True,
                "roles": [{"code": role.code, "name": role.name} for role in user_roles],
                "permissions": ["*"],
                "permission_level": "super_admin"
            }
        
        # 获取具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        logger.info(f"User {user_id} has specific permissions: {len(user_permissions)} items.")
        
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
        logger.debug(f"Checking permission '{required_permission}' for user ID: {user_id}.")
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员拥有所有权限
        if self._is_super_admin(user_roles):
            logger.debug(f"User {user_id} is super admin, permission '{required_permission}' granted.")
            return True
        
        # 检查具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        has_permission = required_permission in user_permissions
        logger.debug(f"User {user_id} has permission '{required_permission}': {has_permission}.")
        return has_permission
    
    async def check_permissions(self, user_id: int, required_permissions: List[str]) -> Dict[str, bool]:
        """
        检查用户是否有指定的多个权限
        返回每个权限的检查结果
        """
        logger.debug(f"Checking multiple permissions {required_permissions} for user ID: {user_id}.")
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员拥有所有权限
        if self._is_super_admin(user_roles):
            logger.debug(f"User {user_id} is super admin, all requested permissions granted.")
            return {perm: True for perm in required_permissions}
        
        # 检查具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        results = {perm: perm in user_permissions for perm in required_permissions}
        logger.debug(f"User {user_id} permission check results: {results}.")
        return results
    
    async def check_any_permission(self, user_id: int, required_permissions: List[str]) -> bool:
        """
        检查用户是否有指定权限中的任意一个
        """
        logger.debug(f"Checking any of permissions {required_permissions} for user ID: {user_id}.")
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员拥有所有权限
        if self._is_super_admin(user_roles):
            logger.debug(f"User {user_id} is super admin, any permission granted.")
            return True
        
        # 检查具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        has_any = any(perm in user_permissions for perm in required_permissions)
        logger.debug(f"User {user_id} has any of permissions {required_permissions}: {has_any}.")
        return has_any
    
    async def check_all_permissions(self, user_id: int, required_permissions: List[str]) -> bool:
        """
        检查用户是否有指定的所有权限
        """
        logger.debug(f"Checking all permissions {required_permissions} for user ID: {user_id}.")
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员拥有所有权限
        if self._is_super_admin(user_roles):
            logger.debug(f"User {user_id} is super admin, all permissions granted.")
            return True
        
        # 检查具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        has_all = all(perm in user_permissions for perm in required_permissions)
        logger.debug(f"User {user_id} has all of permissions {required_permissions}: {has_all}.")
        return has_all
    
    async def get_user_accessible_resources(self, user_id: int, resource_type: str = None) -> List[str]:
        """
        获取用户可访问的资源列表
        """
        logger.debug(f"Getting accessible resources for user {user_id}, resource type: {resource_type}.")
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员可以访问所有资源
        if self._is_super_admin(user_roles):
            logger.debug(f"User {user_id} is super admin, all resources accessible.")
            return ["*"]
        
        # 获取具体权限
        user_permissions = await self._get_user_permissions(user_roles)
        
        if resource_type:
            # 过滤特定类型的资源权限
            accessible_resources = [perm for perm in user_permissions if perm.startswith(f"{resource_type}:")]
            logger.debug(f"User {user_id} accessible {resource_type} resources: {len(accessible_resources)} items.")
            return accessible_resources
        
        logger.debug(f"User {user_id} accessible resources: {len(user_permissions)} items.")
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
        logger.debug(f"Validating data access for user {user_id} to resource owned by {resource_owner_id}, org {resource_org_id}. User org: {user_org_id}.")
        user_roles = await self.role_service.get_user_roles(user_id)
        
        # 超级管理员可以访问所有数据
        if self._is_super_admin(user_roles):
            logger.debug(f"User {user_id} is super admin, data access granted.")
            return True
        
        # 用户可以访问自己的数据
        if user_id == resource_owner_id:
            logger.debug(f"User {user_id} is resource owner, data access granted.")
            return True
        
        # 用户可以访问同组织的数据
        if resource_org_id and user_org_id and resource_org_id == user_org_id:
            logger.debug(f"User {user_id} is in the same organization {user_org_id} as resource {resource_org_id}, data access granted.")
            return True
        
        logger.warning(f"User {user_id} denied data access to resource owned by {resource_owner_id}, org {resource_org_id}.")
        return False
    
    def _is_super_admin(self, user_roles: List[RoleModel]) -> bool:
        """
        检查用户是否是超级管理员
        """
        logger.debug(f"_is_super_admin check for roles: {[role.code for role in user_roles]}.")
        return any(role.code == "super_admin" for role in user_roles)
    
    async def _get_user_permissions(self, user_roles: List[RoleModel]) -> Set[str]:
        """
        获取用户的所有权限
        """
        logger.debug(f"_get_user_permissions for {len(user_roles)} roles.")
        user_permissions = set()
        for role in user_roles:
            role_permissions = await self.role_service.get_role_permissions(role.id)
            user_permissions.update(perm.value for perm in role_permissions)
        logger.debug(f"Collected {len(user_permissions)} unique permissions.")
        return user_permissions
    
    async def get_permission_summary(self, user_id: int) -> Dict:
        """
        获取用户权限摘要信息
        """
        logger.info(f"Getting permission summary for user ID: {user_id}.")
        permission_info = await self.get_user_permission_info(user_id)
        logger.info(f"Returned permission summary for user {user_id}.")
        return {
            "user_id": user_id,
            "is_super_admin": permission_info["is_super_admin"],
            "can_access_all": permission_info["can_access_all"],
            "total_permissions": len(permission_info["permissions"]) if not permission_info["is_super_admin"] else "unlimited",
            "roles_count": len(permission_info["roles"]),
            "permission_level": permission_info["permission_level"]
        }
