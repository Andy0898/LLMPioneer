from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.schemas.role import FunctionPermission, FunctionPermissionCreate, FunctionPermissionUpdate
from app.services.role_service import FunctionPermissionService
from app.db.models.user import UserModel

router = APIRouter()

class PermissionController:
    @staticmethod
    @router.get("/", response_model=Tuple[List[FunctionPermission], int])
    async def list_permissions(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """获取权限列表"""
        permission_service = FunctionPermissionService(db)
        permissions, total = await permission_service.get_permissions(skip, limit)
        return permissions, total

    @staticmethod
    @router.get("/{permission_id}", response_model=FunctionPermission)
    async def get_permission(
        permission_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """获取权限详情"""
        permission_service = FunctionPermissionService(db)
        permission = await permission_service.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return permission

    @staticmethod
    @router.post("/", response_model=FunctionPermission)
    async def create_permission(
        permission_data: FunctionPermissionCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """创建权限"""
        permission_service = FunctionPermissionService(db)
        return await permission_service.create_permission(permission_data, current_user.user_name)

    @staticmethod
    @router.put("/{permission_id}", response_model=FunctionPermission)
    async def update_permission(
        permission_id: int,
        permission_data: FunctionPermissionUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """更新权限"""
        permission_service = FunctionPermissionService(db)
        updated_permission = await permission_service.update_permission(
            permission_id, permission_data, current_user.user_name
        )
        if not updated_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return updated_permission

    @staticmethod
    @router.delete("/{permission_id}")
    async def delete_permission(
        permission_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """删除权限"""
        permission_service = FunctionPermissionService(db)
        if not await permission_service.delete_permission(permission_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return {"message": "Permission deleted successfully"}

    @staticmethod
    @router.post("/{role_id}/permissions")
    async def assign_permissions(
        role_id: int,
        permission_ids: List[int],
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """为角色分配权限"""
        permission_service = FunctionPermissionService(db)
        await permission_service.assign_permissions_to_role(
            role_id, permission_ids, current_user.user_name
        )
        return {"message": "Permissions assigned successfully"} 