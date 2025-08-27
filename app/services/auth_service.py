# app/services/auth.py
from typing import Optional, Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import verify_password, get_password_hash, create_access_token
from app.services.role_service import RoleService
from app.db.models.user import UserModel
from sqlalchemy.orm import selectinload
from app.config.logger import get_logger # 导入日志

logger = get_logger(__name__) # 获取Logger实例

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_service = RoleService(db)
        logger.info("AuthService initialized.")
    
    def _is_super_admin(self, roles: List) -> bool:
        """检查用户是否是超级管理员"""
        logger.debug(f"Checking if user has super_admin role among {len(roles)} roles.")
        return any(role.code == "super_admin" for role in roles)
    
    async def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """用户认证"""
        logger.info(f"Attempting to authenticate user: {username}.")
        result = await self.db.execute(
            select(UserModel)
            .options(selectinload(UserModel.user_roles)) # 修正为 user_roles
            .where(UserModel.user_name == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"Authentication failed for user {username}: User not found.")
            return None
        
        if not verify_password(password, user.password):
            logger.warning(f"Authentication failed for user {username}: Invalid password.")
            return None
            
        if user.is_locked:
            logger.warning(f"Authentication failed for user {username}: Account is locked.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked"
            )
            
        if not user.status:
            logger.warning(f"Authentication failed for user {username}: Account is disabled.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # 获取用户角色和权限
        roles = user.roles  # 直接使用预加载的角色
        is_super_admin = self._is_super_admin(roles)
        logger.debug(f"User {username} roles: {[role.code for role in roles]}, Is Super Admin: {is_super_admin}.")
        
        # 如果是超级管理员，拥有所有权限
        if is_super_admin:
            permissions = ["*"]  # 通配符表示所有权限
            logger.debug(f"User {username} is super admin, granted all permissions.")
        else:
            # 获取用户角色对应的具体权限
            permissions = []
            for role in roles:
                role_permissions = await self.role_service.get_role_permissions(role.id)
                permissions.extend(role_permissions)
            permissions = [perm.value for perm in permissions]
            logger.debug(f"User {username} granted specific permissions: {permissions}.")
        
        # 生成token
        access_token = create_access_token(
            data={
                "sub": user.user_name,
                "user_id": user.id,
                "roles": [role.code for role in roles],
                "permissions": permissions,
                "is_super_admin": is_super_admin
            }
        )
        logger.info(f"User {username} authenticated successfully, access token generated.")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "username": user.user_name,
                "is_super_admin": is_super_admin
            },
            "roles": [{"code": role.code, "name": role.name} for role in roles],
            "permissions": permissions
        }
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        logger.info(f"Attempting to change password for user ID: {user_id}.")
        user = await self.db.get(UserModel, user_id)
        if not user:
            logger.warning(f"Password change failed for user ID {user_id}: User not found.")
            return False
        if not verify_password(old_password, user.password):
            logger.warning(f"Password change failed for user ID {user_id}: Old password mismatch.")
            return False
            
        user.password = get_password_hash(new_password)
        await self.db.commit()
        logger.info(f"Password successfully changed for user ID: {user_id}.")
        return True
    
    async def get_user_permissions(self, user_id: int) -> Dict:
        """获取用户权限信息"""
        logger.info(f"Retrieving permissions for user ID: {user_id}.")
        user = await self.db.get(UserModel, user_id)
        if not user:
            logger.warning(f"Permissions retrieval failed for user ID {user_id}: User not found.")
            return {}
        
        roles = await self.role_service.get_user_roles(user_id)
        is_super_admin = self._is_super_admin(roles)
        logger.debug(f"User {user_id} roles: {[role.code for role in roles]}, Is Super Admin: {is_super_admin}.")
        
        if is_super_admin:
            logger.info(f"User {user_id} is super admin, returning all permissions.")
            return {
                "is_super_admin": True,
                "roles": [{"code": role.code, "name": role.name} for role in roles],
                "permissions": ["*"],  # 超级管理员拥有所有权限
                "can_access_all": True
            }
        else:
            # 获取具体权限
            permissions = []
            for role in roles:
                role_permissions = await self.role_service.get_role_permissions(role.id)
                permissions.extend(role_permissions)
            logger.info(f"User {user_id} has specific permissions: {len(permissions)} items.")
            return {
                "is_super_admin": False,
                "roles": [{"code": role.code, "name": role.name} for role in roles],
                "permissions": [perm.value for perm in permissions],
                "can_access_all": False
            }