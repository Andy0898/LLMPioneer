from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_current_user, require_permissions # 导入 require_permissions
from app.db.session import get_db
from app.schemas.role import FunctionPermission, FunctionPermissionCreate, FunctionPermissionUpdate
from app.services.role_service import FunctionPermissionService
from app.db.models.user import UserModel
from app.config.logger import get_logger # 导入日志

logger = get_logger(__name__) # 获取Logger实例

router = APIRouter()

class PermissionController:
    @staticmethod
    @router.get("/permissions", response_model=Tuple[List[FunctionPermission], int], dependencies=[Depends(require_permissions(["permission:list"]))]) # 添加权限
    async def list_permissions(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """获取权限列表"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) requesting permission list. Skip: {skip}, Limit: {limit}.")
        permission_service = FunctionPermissionService(db)
        permissions, total = await permission_service.get_permissions(skip, limit)
        logger.info(f"Returned {len(permissions)} permissions to user {current_user.id}.")
        return permissions, total

    @staticmethod
    @router.get("/{permission_id}", response_model=FunctionPermission, dependencies=[Depends(require_permissions(["permission:read"]))]) # 添加权限
    async def get_permission(
        permission_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """获取权限详情"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) requesting detail for permission {permission_id}.")
        permission_service = FunctionPermissionService(db)
        permission = await permission_service.get_permission_by_id(permission_id)
        if not permission:
            logger.warning(f"Permission {permission_id} not found for detail request by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        logger.info(f"Returned detail for permission {permission_id} to user {current_user.id}.")
        return permission

    @staticmethod
    @router.post("/add", response_model=FunctionPermission, dependencies=[Depends(require_permissions(["permission:create"]))]) # 添加权限
    async def create_permission(
        permission_data: FunctionPermissionCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """创建权限"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to create permission: {permission_data.name} ({permission_data.value}).")
        permission_service = FunctionPermissionService(db)
        new_permission = await permission_service.create_permission(permission_data, current_user.user_name)
        logger.info(f"Permission {new_permission.id} ({new_permission.name}) created by user {current_user.id}.")
        return new_permission

    @staticmethod
    @router.put("/{permission_id}", response_model=FunctionPermission, dependencies=[Depends(require_permissions(["permission:update"]))]) # 添加权限
    async def update_permission(
        permission_id: int,
        permission_data: FunctionPermissionUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """更新权限"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to update permission {permission_id} with data: {permission_data.dict()}")
        permission_service = FunctionPermissionService(db)
        updated_permission = await permission_service.update_permission(
            permission_id, permission_data, current_user.user_name
        )
        if not updated_permission:
            logger.warning(f"Permission {permission_id} not found for update by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        logger.info(f"Permission {permission_id} updated by user {current_user.id}.")
        return updated_permission

    @staticmethod
    @router.delete("/{permission_id}", dependencies=[Depends(require_permissions(["permission:delete"]))]) # 添加权限
    async def delete_permission(
        permission_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """删除权限"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to delete permission {permission_id}.")
        permission_service = FunctionPermissionService(db)
        if not await permission_service.delete_permission(permission_id):
            logger.warning(f"Permission {permission_id} not found for deletion by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        logger.info(f"Permission {permission_id} deleted by user {current_user.id}.")
        return {"message": "Permission deleted successfully"}

    @staticmethod
    @router.post("/{role_id}/permissions", dependencies=[Depends(require_permissions(["permission:assign"]))]) # 添加权限
    async def assign_permissions(
        role_id: int,
        permission_ids: List[int],
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """为角色分配权限"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to assign permissions {permission_ids} to role {role_id}.")
        permission_service = FunctionPermissionService(db)
        await permission_service.assign_permissions_to_role(
            role_id, permission_ids, current_user.user_name
        )
        logger.info(f"Permissions {permission_ids} assigned to role {role_id} by user {current_user.id}.")
        return {"message": "Permissions assigned successfully"} 