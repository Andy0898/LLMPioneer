from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.config.settings import settings
from app.db.session import get_db
from app.core.security import verify_token
from app.db.models import UserModel
from app.services.role_service import RoleService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.API_V1_STR+"/auth/login")

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
        .options(selectinload(UserModel.user_roles))
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

async def get_current_user_with_permissions(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取当前用户及其权限信息
    """
    role_service = RoleService(db)
    # 从预加载的用户角色中获取角色信息，避免懒加载
    user_roles = []
    for user_role in current_user.user_roles:
        if user_role.role:
            user_roles.append(user_role.role)
    # user_roles = await role_service.get_user_roles(current_user.id)
    
    # 检查是否是超级管理员
    is_super_admin = any(role.code == "super_admin" for role in user_roles)
    
    if is_super_admin:
        return {
            "user": current_user,
            "is_super_admin": True,
            "can_access_all": True,
            "roles": user_roles,
            "permissions": ["*"]
        }
    
    # 获取具体权限
    user_permissions = set()
    for role in user_roles:
        permissions = await role_service.get_role_permissions(role.id)
        user_permissions.update(perm.value for perm in permissions)
    
    return {
        "user": current_user,
        "is_super_admin": False,
        "can_access_all": False,
        "roles": user_roles,
        "permissions": list(user_permissions)
    }

def require_permissions(required_permissions: List[str]):
    """
    权限验证依赖 - 支持超级管理员和具体权限检查
    """
    async def permission_dependency(
        current_user: UserModel = Security(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        role_service = RoleService(db)
        # user_roles = await role_service.get_user_roles(current_user.id)
                # 从预加载的用户角色中获取角色信息
        user_roles = []
        for user_role in current_user.user_roles:
            if user_role.role:
                user_roles.append(user_role.role)
        
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
                detail=f"Permission denied. Required: {required_permissions}, Available: {list(user_permissions)}"
            )
        return current_user
    
    return permission_dependency

def require_super_admin():
    """
    要求超级管理员权限的依赖
    """
    async def super_admin_dependency(
        current_user: UserModel = Security(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        role_service = RoleService(db)
        # user_roles = await role_service.get_user_roles(current_user.id)
        # 从预加载的用户角色中获取角色信息
        user_roles = []
        for user_role in current_user.user_roles:
            if user_role.role:
                user_roles.append(user_role.role)
        
        # 检查是否是超级管理员
        if not any(role.code == "super_admin" for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin permission required"
            )
        return current_user
    
    return super_admin_dependency

def check_data_access_permission(
    resource_owner_id: int = None,
    resource_org_id: int = None
):
    """
    检查数据访问权限的依赖
    支持超级管理员访问所有数据，普通用户只能访问自己或组织内的数据
    """
    async def data_access_dependency(
        current_user: UserModel = Security(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        role_service = RoleService(db)
        # user_roles = await role_service.get_user_roles(current_user.id)
        # 从预加载的用户角色中获取角色信息
        user_roles = []
        for user_role in current_user.user_roles:
            if user_role.role:
                user_roles.append(user_role.role)
        
        # 超级管理员可以访问所有数据
        if any(role.code == "super_admin" for role in user_roles):
            return current_user
        
        # 普通用户只能访问自己的数据或组织内的数据
        if resource_owner_id and resource_owner_id == current_user.id:
            return current_user
            
        if resource_org_id and hasattr(current_user, 'org_id') and resource_org_id == current_user.org_id:
            return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resource"
        )
    
    return data_access_dependency

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