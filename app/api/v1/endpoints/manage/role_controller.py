from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.schemas.role import Role, RoleCreate, RoleUpdate, RoleWithPermissions
from app.services.role_service import RoleService
from app.db.models.user import UserModel

router = APIRouter()

class RoleController:
    @staticmethod
    @router.get("/roles", response_model=Tuple[List[Role], int])
    async def list_roles(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """获取角色列表"""
        role_service = RoleService(db)
        roles, total = await role_service.get_roles(skip, limit)
        return roles, total

    @staticmethod
    @router.get("/{role_id}", response_model=RoleWithPermissions)
    async def get_role(
        role_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """获取角色详情"""
        role_service = RoleService(db)
        role = await role_service.get_role_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        permissions = await role_service.get_role_permissions(role_id)
        return {
            **role.__dict__,
            "permissions": permissions
        }

    @staticmethod
    @router.post("/add", response_model=Role)
    async def create_role(
        role_data: RoleCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """创建角色"""
        role_service = RoleService(db)
        existing_role = await role_service.get_role_by_code(role_data.code)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role code already exists"
            )
        return await role_service.create_role(role_data, current_user.user_name)

    @staticmethod
    @router.put("/{role_id}", response_model=Role)
    async def update_role(
        role_id: int,
        role_data: RoleUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """更新角色"""
        role_service = RoleService(db)
        updated_role = await role_service.update_role(role_id, role_data, current_user.user_name)
        if not updated_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return updated_role

    @staticmethod
    @router.delete("/{role_id}")
    async def delete_role(
        role_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
    ):
        """删除角色"""
        role_service = RoleService(db)
        if not await role_service.delete_role(role_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return {"message": "Role deleted successfully"} 