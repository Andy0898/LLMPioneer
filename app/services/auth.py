# app/services/auth.py
from typing import Optional, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import verify_password, get_password_hash, create_access_token
from app.services.role import RoleService
from app.db.models.user import UserModel
from sqlalchemy.orm import selectinload

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_service = RoleService(db)
    
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
        permissions = []
        for role in roles:
            role_permissions = await self.role_service.get_role_permissions(role.id)
            permissions.extend(role_permissions)
        
        # 生成token
        access_token = create_access_token(
            data={
                "sub": user.user_name,
                "user_id": user.id,
                "roles": [role.code for role in roles],
                "permissions": [perm.value for perm in permissions]
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "roles": [{"code": role.code, "name": role.name} for role in roles],
            "permissions": [perm.value for perm in permissions]
        }
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        user = await self.db.get(UserModel, user_id)
        if not user or not verify_password(old_password, user.password):
            return False
            
        user.password = get_password_hash(new_password)
        await self.db.commit()
        return True