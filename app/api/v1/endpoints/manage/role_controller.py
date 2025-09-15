from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_current_user, require_permissions # 导入 require_permissions
from app.db.session import get_db
from app.schemas.role import Role, RoleCreate, RoleUpdate, RoleWithPermissions
from app.services.role_service import RoleService
from app.db.models.user import UserModel
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

router = APIRouter()

class RoleController:
    @staticmethod
    @router.get("/roles", response_model=Tuple[List[Role], int], dependencies=[Depends(require_permissions(["role:list"]))]) # 添加权限
    async def list_roles(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """获取角色列表"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) requesting role list. Skip: {skip}, Limit: {limit}.")
        role_service = RoleService(db)
        roles, total = await role_service.get_roles(skip, limit)
        logger.info(f"Returned {len(roles)} roles to user {current_user.id}.")
        return roles, total

    @staticmethod
    @router.get("/{role_id}", response_model=RoleWithPermissions, dependencies=[Depends(require_permissions(["role:read"]))]) # 添加权限
    async def get_role(
        role_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """获取角色详情"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) requesting detail for role {role_id}.")
        role_service = RoleService(db)
        role = await role_service.get_role_by_id(role_id)
        if not role:
            logger.warning(f"Role {role_id} not found for detail request by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        permissions = await role_service.get_role_permissions(role_id)
        logger.info(f"Returned detail for role {role_id} with {len(permissions)} permissions to user {current_user.id}.")
        return {
            **role.__dict__,
            "permissions": permissions
        }

    @staticmethod
    @router.post("/add", response_model=Role, dependencies=[Depends(require_permissions(["role:create"]))]) # 添加权限
    async def create_role(
        role_data: RoleCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """创建角色"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to create role: {role_data.name} ({role_data.code}).")
        role_service = RoleService(db)
        existing_role = await role_service.get_role_by_code(role_data.code)
        if existing_role:
            logger.warning(f"Attempted to create role with existing code {role_data.code} by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role code already exists"
            )
        new_role = await role_service.create_role(role_data, current_user.user_name)
        logger.info(f"Role {new_role.id} ({new_role.name}) created by user {current_user.id}.")
        return new_role

    @staticmethod
    @router.put("/{role_id}", response_model=Role, dependencies=[Depends(require_permissions(["role:update"]))]) # 添加权限
    async def update_role(
        role_id: int,
        role_data: RoleUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """更新角色"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to update role {role_id} with data: {role_data.dict()}")
        role_service = RoleService(db)
        updated_role = await role_service.update_role(role_id, role_data, current_user.user_name)
        if not updated_role:
            logger.warning(f"Role {role_id} not found for update by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        logger.info(f"Role {role_id} updated by user {current_user.id}.")
        return updated_role

    @staticmethod
    @router.delete("/{role_id}", dependencies=[Depends(require_permissions(["role:delete"]))]) # 添加权限
    async def delete_role(
        role_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """删除角色"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to delete role {role_id}.")
        role_service = RoleService(db)
        if not await role_service.delete_role(role_id):
            logger.warning(f"Role {role_id} not found for deletion by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        logger.info(f"Role {role_id} deleted by user {current_user.id}.")
        return {"message": "Role deleted successfully"} 