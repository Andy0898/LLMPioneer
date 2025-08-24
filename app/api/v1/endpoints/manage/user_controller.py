from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import (
    get_db,
    require_permissions
)
from app.db.models.user import UserModel
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user import UserService

router = APIRouter()

class UserController:
    @staticmethod
    @router.get("/users", response_model=Tuple[List[User], int])
    async def list_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(require_permissions(["user:list"]))
    ) -> Tuple[List[UserModel], int]:
        """获取用户列表"""
        user_service = UserService(db)
        users, total = await user_service.get_users(skip=skip, limit=limit)
        # 确保每个用户对象都被正确序列化
        return [User.model_validate(user) for user in users], total

    @staticmethod
    @router.get("/users/{user_id}", response_model=User)
    async def get_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(require_permissions(["user:read"]))
    ) -> UserModel:
        """获取用户详情"""
        user_service = UserService(db)
        user = await user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @staticmethod
    @router.post("/users", response_model=User)
    async def create_user(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(require_permissions(["user:create"]))
    ) -> UserModel:
        """创建用户"""
        user_service = UserService(db)
        # 检查用户名是否已存在
        if await user_service.get_by_username(user_data.user_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        return await user_service.create(user_data, current_user.user_name)

    @staticmethod
    @router.put("/users/{user_id}", response_model=User)
    async def update_user(
        user_id: int,
        user_data: UserUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(require_permissions(["user:update"]))
    ) -> UserModel:
        """更新用户"""
        user_service = UserService(db)
        updated_user = await user_service.update(user_id, user_data, current_user.user_name)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user

    @staticmethod
    @router.delete("/users/{user_id}", response_model=bool)
    async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(require_permissions(["user:delete"]))
    ) -> bool:
        """删除用户"""
        # 不允许删除自己
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete yourself"
            )
        
        user_service = UserService(db)
        if not await user_service.delete(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return True 