# app/services/role.py
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import UserRoleModel, RoleModel, FunctionPermissionModel, RolePermissionModel
from app.schemas.role import RoleCreate, RoleUpdate, FunctionPermissionCreate, FunctionPermissionUpdate
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info("RoleService initialized.")
    
    async def get_role_by_id(self, role_id: int) -> Optional[RoleModel]:
        """通过ID获取角色"""
        logger.debug(f"Fetching role by ID: {role_id}.")
        role = await self.db.get(RoleModel, role_id)
        if role:
            logger.debug(f"Role {role_id} found.")
        else:
            logger.debug(f"Role {role_id} not found.")
        return role
    
    async def get_role_by_code(self, code: str) -> Optional[RoleModel]:
        """通过编码获取角色"""
        logger.debug(f"Fetching role by code: {code}.")
        result = await self.db.execute(
            select(RoleModel).where(RoleModel.code == code)
        )
        role = result.scalar_one_or_none()
        if role:
            logger.debug(f"Role with code {code} found.")
        else:
            logger.debug(f"Role with code {code} not found.")
        return role
    
    async def get_roles(self, skip: int = 0, limit: int = 10) -> Tuple[List[RoleModel], int]:
        """获取角色列表"""
        logger.debug(f"Fetching roles. Skip: {skip}, Limit: {limit}.")
        query = select(RoleModel)
        total = await self.db.scalar(
            select(func.count()).select_from(query.subquery())
        )
        
        result = await self.db.execute(
            query.offset(skip).limit(limit)
        )
        roles = result.scalars().all()
        logger.debug(f"Returned {len(roles)} roles (total: {total}).")
        return roles, total
    
    async def create_role(self, role_data: RoleCreate, operator: str) -> RoleModel:
        """创建角色"""
        logger.info(f"User {operator} attempting to create role: {role_data.name} ({role_data.code}).")
        db_role = RoleModel(
            code=role_data.code,
            name=role_data.name,
            org_id=role_data.org_id,
            create_by=operator
        )
        self.db.add(db_role)
        await self.db.commit()
        await self.db.refresh(db_role)
        logger.info(f"Role {db_role.id} ({db_role.name}) created successfully by {operator}.")
        return db_role
    
    async def update_role(self, role_id: int, role_data: RoleUpdate, operator: str) -> Optional[RoleModel]:
        """更新角色"""
        logger.info(f"User {operator} attempting to update role {role_id} with data: {role_data.dict(exclude_unset=True)}.")
        db_role = await self.get_role_by_id(role_id)
        if not db_role:
            logger.warning(f"Role {role_id} not found for update by {operator}.")
            return None
            
        for field, value in role_data.dict(exclude_unset=True).items():
            setattr(db_role, field, value)
        db_role.update_by = operator
        
        await self.db.commit()
        await self.db.refresh(db_role)
        logger.info(f"Role {role_id} updated successfully by {operator}.")
        return db_role
    
    async def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        logger.info(f"Attempting to delete role {role_id}.")
        db_role = await self.get_role_by_id(role_id)
        if not db_role:
            logger.warning(f"Role {role_id} not found for deletion.")
            return False
            
        await self.db.delete(db_role)
        await self.db.commit()
        logger.info(f"Role {role_id} deleted successfully.")
        return True
    
    async def get_user_roles(self, user_id: int) -> List[RoleModel]:
        """获取用户的所有角色"""
        logger.debug(f"Fetching roles for user ID: {user_id}.")
        result = await self.db.execute(
            select(RoleModel)
            .join(UserRoleModel)
            .where(UserRoleModel.user_id == user_id)
        )
        roles = result.scalars().all()
        logger.debug(f"Returned {len(roles)} roles for user {user_id}.")
        return roles
    
    async def get_role_permissions(self, role_id: int) -> List[FunctionPermissionModel]:
        """获取角色的所有权限"""
        logger.debug(f"Fetching permissions for role ID: {role_id}.")
        result = await self.db.execute(
            select(FunctionPermissionModel)
            .join(RolePermissionModel)
            .where(RolePermissionModel.role_id == role_id)
        )
        permissions = result.scalars().all()
        logger.debug(f"Returned {len(permissions)} permissions for role {role_id}.")
        return permissions

class FunctionPermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info("FunctionPermissionService initialized.")
    
    async def get_permission_by_id(self, permission_id: int) -> Optional[FunctionPermissionModel]:
        """通过ID获取权限"""
        logger.debug(f"Fetching function permission by ID: {permission_id}.")
        permission = await self.db.get(FunctionPermissionModel, permission_id)
        if permission:
            logger.debug(f"Function permission {permission_id} found.")
        else:
            logger.debug(f"Function permission {permission_id} not found.")
        return permission
    
    async def get_permissions(
        self, skip: int = 0, limit: int = 10
    ) -> Tuple[List[FunctionPermissionModel], int]:
        """获取权限列表"""
        logger.debug(f"Fetching function permissions. Skip: {skip}, Limit: {limit}.")
        query = select(FunctionPermissionModel)
        total = await self.db.scalar(
            select(func.count()).select_from(query.subquery())
        )
        
        result = await self.db.execute(
            query.offset(skip).limit(limit)
        )
        permissions = result.scalars().all()
        logger.debug(f"Returned {len(permissions)} function permissions (total: {total}).")
        return permissions, total
    
    async def create_permission(
        self, permission_data: FunctionPermissionCreate, operator: str
    ) -> FunctionPermissionModel:
        """创建权限"""
        logger.info(f"User {operator} attempting to create function permission: {permission_data.name} ({permission_data.value}).")
        db_permission = FunctionPermissionModel(
            **permission_data.dict(),
            create_by=operator
        )
        self.db.add(db_permission)
        await self.db.commit()
        await self.db.refresh(db_permission)
        logger.info(f"Function permission {db_permission.id} ({db_permission.name}) created successfully by {operator}.")
        return db_permission
    
    async def update_permission(
        self, permission_id: int, permission_data: FunctionPermissionUpdate, operator: str
    ) -> Optional[FunctionPermissionModel]:
        """更新权限"""
        logger.info(f"User {operator} attempting to update function permission {permission_id} with data: {permission_data.dict(exclude_unset=True)}.")
        db_permission = await self.get_permission_by_id(permission_id)
        if not db_permission:
            logger.warning(f"Function permission {permission_id} not found for update by {operator}.")
            return None
            
        for field, value in permission_data.dict(exclude_unset=True).items():
            setattr(db_permission, field, value)
        db_permission.update_by = operator
        
        await self.db.commit()
        await self.db.refresh(db_permission)
        logger.info(f"Function permission {permission_id} updated successfully by {operator}.")
        return db_permission
    
    async def delete_permission(self, permission_id: int) -> bool:
        """删除权限"""
        logger.info(f"Attempting to delete function permission {permission_id}.")
        db_permission = await self.get_permission_by_id(permission_id)
        if not db_permission:
            logger.warning(f"Function permission {permission_id} not found for deletion.")
            return False
            
        await self.db.delete(db_permission)
        await self.db.commit()
        logger.info(f"Function permission {permission_id} deleted successfully.")
        return True
    
    async def assign_permissions_to_role(
        self, role_id: int, permission_ids: List[int], operator: str
    ) -> bool:
        """为角色分配权限"""
        logger.info(f"User {operator} attempting to assign permissions {permission_ids} to role {role_id}.")
        # 先删除原有的权限
        await self.db.execute(
            RolePermissionModel.__table__.delete().where(
                RolePermissionModel.role_id == role_id
            )
        )
        logger.debug(f"Existing permissions for role {role_id} cleared.")
        
        # 添加新的权限
        for permission_id in permission_ids:
            self.db.add(RolePermissionModel(
                role_id=role_id,
                func_per_id=permission_id
            ))
        
        await self.db.commit()
        logger.info(f"Permissions {permission_ids} assigned to role {role_id} successfully by {operator}.")
        return True

