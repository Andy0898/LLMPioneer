# app/api/v1/endpoints/permission_demo_controller.py
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import (
    get_current_user, 
    require_permissions, 
    require_super_admin,
    get_current_user_with_permissions,
    check_data_access_permission
)
from app.db.session import get_db
from app.services.permission_manager import PermissionManager
from app.db.models import UserModel

router = APIRouter()

@router.get("/my-permissions")
async def get_my_permissions(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的权限信息
    """
    permission_manager = PermissionManager(db)
    permission_info = await permission_manager.get_user_permission_info(current_user.id)
    
    return {
        "message": "权限信息获取成功",
        "data": permission_info
    }

@router.get("/permission-summary")
async def get_permission_summary(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的权限摘要
    """
    permission_manager = PermissionManager(db)
    summary = await permission_manager.get_permission_summary(current_user.id)
    
    return {
        "message": "权限摘要获取成功",
        "data": summary
    }

@router.get("/check-permission/{permission}")
async def check_specific_permission(
    permission: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    检查当前用户是否有指定权限
    """
    permission_manager = PermissionManager(db)
    has_permission = await permission_manager.check_permission(current_user.id, permission)
    
    return {
        "message": "权限检查完成",
        "data": {
            "permission": permission,
            "has_permission": has_permission,
            "user_id": current_user.id
        }
    }

@router.post("/check-multiple-permissions")
async def check_multiple_permissions(
    permissions: List[str],
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    检查当前用户是否有指定的多个权限
    """
    permission_manager = PermissionManager(db)
    results = await permission_manager.check_permissions(current_user.id, permissions)
    
    return {
        "message": "多权限检查完成",
        "data": {
            "permissions": permissions,
            "results": results,
            "user_id": current_user.id
        }
    }

@router.get("/super-admin-only")
async def super_admin_only_endpoint(
    current_user: UserModel = Depends(require_super_admin())
):
    """
    只有超级管理员才能访问的端点
    """
    return {
        "message": "超级管理员访问成功",
        "data": {
            "user_id": current_user.id,
            "username": current_user.user_name,
            "access_level": "super_admin"
        }
    }

@router.get("/user-management")
async def user_management_endpoint(
    current_user: UserModel = Depends(require_permissions(["user:read", "user:manage"]))
):
    """
    需要用户管理权限的端点
    """
    return {
        "message": "用户管理功能访问成功",
        "data": {
            "user_id": current_user.id,
            "username": current_user.user_name,
            "required_permissions": ["user:read", "user:manage"]
        }
    }

@router.get("/document-access/{document_id}")
async def document_access_endpoint(
    document_id: int,
    current_user: UserModel = Depends(check_data_access_permission(resource_owner_id=document_id))
):
    """
    检查数据访问权限的端点
    """
    return {
        "message": "文档访问权限验证成功",
        "data": {
            "document_id": document_id,
            "user_id": current_user.id,
            "access_granted": True
        }
    }

@router.get("/accessible-resources")
async def get_accessible_resources(
    resource_type: str = None,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户可访问的资源列表
    """
    permission_manager = PermissionManager(db)
    resources = await permission_manager.get_user_accessible_resources(
        current_user.id, 
        resource_type
    )
    
    return {
        "message": "可访问资源获取成功",
        "data": {
            "user_id": current_user.id,
            "resource_type": resource_type,
            "accessible_resources": resources
        }
    }

@router.get("/permission-test")
async def permission_test_endpoint(
    user_info: Dict = Depends(get_current_user_with_permissions)
):
    """
    测试权限依赖注入的端点
    """
    return {
        "message": "权限测试成功",
        "data": {
            "user": {
                "id": user_info["user"].id,
                "username": user_info["user"].user_name
            },
            "permission_info": {
                "is_super_admin": user_info["is_super_admin"],
                "can_access_all": user_info["can_access_all"],
                "roles_count": len(user_info["roles"]),
                "permissions_count": len(user_info["permissions"]) if not user_info["is_super_admin"] else "unlimited"
            }
        }
    }
