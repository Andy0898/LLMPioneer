# app/services/role.py
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.role import RoleModel, FunctionPermissionModel, RoleFunctionPermissionModel, UserRoleModel
from app.schemas.role import RoleCreate, RoleUpdate, FunctionPermissionCreate, FunctionPermissionUpdate

class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_role_by_id(self, role_id: int) -> Optional[RoleModel]:
        """通过ID获取角色"""
        return await self.db.get(RoleModel, role_id)
    
    async def get_role_by_code(self, code: str) -> Optional[RoleModel]:
        """通过编码获取角色"""
        result = await self.db.execute(
            select(RoleModel).where(RoleModel.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_roles(self, skip: int = 0, limit: int = 10) -> Tuple[List[RoleModel], int]:
        """获取角色列表"""
        query = select(RoleModel)
        total = await self.db.scalar(
            select(func.count()).select_from(query.subquery())
        )
        
        result = await self.db.execute(
            query.offset(skip).limit(limit)
        )
        return result.scalars().all(), total
    
    async def create_role(self, role_data: RoleCreate, operator: str) -> RoleModel:
        """创建角色"""
        db_role = RoleModel(
            code=role_data.code,
            name=role_data.name,
            org_id=role_data.org_id,
            create_by=operator
        )
        self.db.add(db_role)
        await self.db.commit()
        await self.db.refresh(db_role)
        return db_role
    
    async def update_role(self, role_id: int, role_data: RoleUpdate, operator: str) -> Optional[RoleModel]:
        """更新角色"""
        db_role = await self.get_role_by_id(role_id)
        if not db_role:
            return None
            
        for field, value in role_data.dict(exclude_unset=True).items():
            setattr(db_role, field, value)
        db_role.update_by = operator
        
        await self.db.commit()
        await self.db.refresh(db_role)
        return db_role
    
    async def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        db_role = await self.get_role_by_id(role_id)
        if not db_role:
            return False
            
        await self.db.delete(db_role)
        await self.db.commit()
        return True
    
    async def get_user_roles(self, user_id: int) -> List[RoleModel]:
        """获取用户的所有角色"""
        result = await self.db.execute(
            select(RoleModel)
            .join(UserRoleModel)
            .where(UserRoleModel.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_role_permissions(self, role_id: int) -> List[FunctionPermissionModel]:
        """获取角色的所有权限"""
        result = await self.db.execute(
            select(FunctionPermissionModel)
            .join(RoleFunctionPermissionModel)
            .where(RoleFunctionPermissionModel.role_id == role_id)
        )
        return result.scalars().all()

class FunctionPermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_permission_by_id(self, permission_id: int) -> Optional[FunctionPermissionModel]:
        """通过ID获取权限"""
        return await self.db.get(FunctionPermissionModel, permission_id)
    
    async def get_permissions(
        self, skip: int = 0, limit: int = 10
    ) -> Tuple[List[FunctionPermissionModel], int]:
        """获取权限列表"""
        query = select(FunctionPermissionModel)
        total = await self.db.scalar(
            select(func.count()).select_from(query.subquery())
        )
        
        result = await self.db.execute(
            query.offset(skip).limit(limit)
        )
        return result.scalars().all(), total
    
    async def create_permission(
        self, permission_data: FunctionPermissionCreate, operator: str
    ) -> FunctionPermissionModel:
        """创建权限"""
        db_permission = FunctionPermissionModel(
            **permission_data.dict(),
            create_by=operator
        )
        self.db.add(db_permission)
        await self.db.commit()
        await self.db.refresh(db_permission)
        return db_permission
    
    async def update_permission(
        self, permission_id: int, permission_data: FunctionPermissionUpdate, operator: str
    ) -> Optional[FunctionPermissionModel]:
        """更新权限"""
        db_permission = await self.get_permission_by_id(permission_id)
        if not db_permission:
            return None
            
        for field, value in permission_data.dict(exclude_unset=True).items():
            setattr(db_permission, field, value)
        db_permission.update_by = operator
        
        await self.db.commit()
        await self.db.refresh(db_permission)
        return db_permission
    
    async def delete_permission(self, permission_id: int) -> bool:
        """删除权限"""
        db_permission = await self.get_permission_by_id(permission_id)
        if not db_permission:
            return False
            
        await self.db.delete(db_permission)
        await self.db.commit()
        return True
    
    async def assign_permissions_to_role(
        self, role_id: int, permission_ids: List[int], operator: str
    ) -> bool:
        """为角色分配权限"""
        # 先删除原有的权限
        await self.db.execute(
            RoleFunctionPermissionModel.__table__.delete().where(
                RoleFunctionPermissionModel.role_id == role_id
            )
        )
        
        # 添加新的权限
        for permission_id in permission_ids:
            self.db.add(RoleFunctionPermissionModel(
                role_id=role_id,
                func_per_id=permission_id
            ))
        
        await self.db.commit()
        return True

