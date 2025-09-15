from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import CONFIG as settings
from functools import wraps
from fastapi import HTTPException, status
from app.services.role_service import RoleService
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.security.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Union[dict, None]:
    """
    验证令牌
    """
    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        return payload
    except JWTError:
        return None 

def require_permissions(permissions: List[str]):
    """
    权限验证装饰器 - 支持超级管理员和具体权限检查
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            db = kwargs.get('db')
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not available"
                )
            
            role_service = RoleService(db)
            user_roles = await role_service.get_user_roles(current_user.id)
            
            # 检查是否是超级管理员
            is_super_admin = any(role.code == "super_admin" for role in user_roles)
            
            # 如果是超级管理员，直接放行
            if is_super_admin:
                return await func(*args, **kwargs)
            
            # 获取用户所有权限
            user_permissions = set()
            for role in user_roles:
                role_permissions = await role_service.get_role_permissions(role.id)
                user_permissions.update(perm.value for perm in role_permissions)
            
            # 检查是否有所需权限
            if not any(p in user_permissions for p in permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {permissions}, Available: {list(user_permissions)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_super_admin():
    """
    要求超级管理员权限的装饰器
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            db = kwargs.get('db')
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not available"
                )
            
            role_service = RoleService(db)
            user_roles = await role_service.get_user_roles(current_user.id)
            
            # 检查是否是超级管理员
            is_super_admin = any(role.code == "super_admin" for role in user_roles)
            
            if not is_super_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Super admin permission required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def check_permission(required_permission: str, user_permissions: List[str], is_super_admin: bool = False) -> bool:
    """
    检查用户是否有指定权限
    """
    if is_super_admin:
        return True
    
    return required_permission in user_permissions

def get_user_permission_level(user_roles: List, user_permissions: List[str]) -> dict:
    """
    获取用户权限级别信息
    """
    is_super_admin = any(role.code == "super_admin" for role in user_roles)
    
    return {
        "is_super_admin": is_super_admin,
        "can_access_all": is_super_admin,
        "available_permissions": user_permissions if not is_super_admin else ["*"],
        "role_codes": [role.code for role in user_roles]
    }

class PermissionMiddleware:
    """
    权限中间件 - 用于自动检查API权限
    """
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 检查是否需要权限验证
            path = scope.get("path", "")
            method = scope.get("method", "")
            
            # 跳过不需要权限验证的路径
            if self._should_skip_permission_check(path):
                await self.app(scope, receive, send)
                return
            
            # 这里可以添加更多的权限检查逻辑
            # 例如：检查路径是否在用户的权限列表中
        
        await self.app(scope, receive, send)
    
    def _should_skip_permission_check(self, path: str) -> bool:
        """判断是否跳过权限检查"""
        skip_paths = [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/auth/login",
            "/auth/register",
            "/health"
        ]
        return any(path.startswith(skip_path) for skip_path in skip_paths)

def create_permission_filter(allowed_permissions: List[str]):
    """
    创建权限过滤器
    """
    def filter_function(user_permissions: List[str], is_super_admin: bool = False) -> bool:
        if is_super_admin:
            return True
        return any(perm in user_permissions for perm in allowed_permissions)
    
    return filter_function

def validate_resource_access(
    user_id: int,
    resource_owner_id: int,
    user_roles: List,
    resource_org_id: int = None,
    user_org_id: int = None
) -> bool:
    """
    验证资源访问权限
    """
    # 超级管理员可以访问所有资源
    if any(role.code == "super_admin" for role in user_roles):
        return True
    
    # 用户可以访问自己的资源
    if user_id == resource_owner_id:
        return True
    
    # 用户可以访问同组织的资源（如果组织ID存在）
    if resource_org_id and user_org_id and resource_org_id == user_org_id:
        return True
    
    return False
