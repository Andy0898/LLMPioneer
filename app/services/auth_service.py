# app/services/auth.py
from typing import Optional, Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import verify_password, get_password_hash, create_access_token
from app.services.role_service import RoleService
from app.db.models.user import UserModel
from sqlalchemy.orm import selectinload

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_service = RoleService(db)
    
    def _is_super_admin(self, roles: List) -> bool:
        """检查用户是否是超级管理员"""
        return any(role.code == "super_admin" for role in roles)
    
    async def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """用户认证"""
        result = await self.db.execute(
            select(UserModel)
            .options(selectinload(UserModel.user_roles))
            .where(UserModel.user_name == username)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.password):            
            return None
            
        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked"
            )
            
        if not user.status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # 获取用户角色和权限
        roles = user.roles  # 直接使用预加载的角色
        is_super_admin = self._is_super_admin(roles)
        
        # 如果是超级管理员，拥有所有权限
        if is_super_admin:
            permissions = ["*"]  # 通配符表示所有权限
        else:
            # 获取用户角色对应的具体权限
            permissions = []
            for role in roles:
                role_permissions = await self.role_service.get_role_permissions(role.id)
                permissions.extend(role_permissions)
            permissions = [perm.value for perm in permissions]
        
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
        user = await self.db.get(UserModel, user_id)
        if not user or not verify_password(old_password, user.password):
            return False
            
        user.password = get_password_hash(new_password)
        await self.db.commit()
        return True
    
    async def get_user_permissions(self, user_id: int) -> Dict:
        """获取用户权限信息"""
        user = await self.db.get(UserModel, user_id)
        if not user:
            return {}
        
        roles = await self.role_service.get_user_roles(user_id)
        is_super_admin = self._is_super_admin(roles)
        
        if is_super_admin:
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
            
            return {
                "is_super_admin": False,
                "roles": [{"code": role.code, "name": role.name} for role in roles],
                "permissions": [perm.value for perm in permissions],
                "can_access_all": False
            }