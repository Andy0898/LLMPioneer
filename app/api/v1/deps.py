from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.core.security import verify_token
from app.db.models.user import UserModel
from app.services.role import RoleService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    获取当前用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
        
    user_name: str = payload.get("sub")
    if user_name is None:
        raise credentials_exception
        
    result = await db.execute(
        select(UserModel)
        .options(selectinload(UserModel.roles))
        .where(UserModel.user_name == user_name)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
        
    if not user.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled"
        )
        
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    获取当前活跃用户
    """
    if not current_user.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

def require_permissions(required_permissions: List[str]):
    """
    权限验证装饰器
    """
    async def permission_dependency(
        current_user: UserModel = Security(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        # 检查是否是超级管理员
        role_service = RoleService(db)
        user_roles = await role_service.get_user_roles(current_user.id)
        
        # 如果用户是超级管理员，直接放行
        if any(role.code == "super_admin" for role in user_roles):
            return current_user
            
        # 获取用户所有权限
        user_permissions = set()
        for role in user_roles:
            permissions = await role_service.get_role_permissions(role.id)
            user_permissions.update(perm.value for perm in permissions)
        
        # 检查是否有所需权限
        if not any(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return current_user
    
    return permission_dependency

import redis
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)

def get_redis():
    """
    Dependency to check Redis connection and return a client.
    Raises HTTPException if connection fails.
    """
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_connect_timeout=1,  # Set a timeout to avoid long waits
        )
        redis_client.ping()
        yield redis_client
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service is unavailable."
        ) 