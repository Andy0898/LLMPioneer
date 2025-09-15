from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import (
    get_db,
    require_permissions
)
from app.db.models.user import UserModel
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

router = APIRouter()

class UserController:
    @staticmethod
    @router.get("/users", response_model=Tuple[List[User], int], dependencies=[Depends(require_permissions(["user:list"]))]) # 添加权限
    async def list_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(require_permissions(["user:list"]))
    ) -> Tuple[List[UserModel], int]:
        """获取用户列表"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) requesting user list. Skip: {skip}, Limit: {limit}.")
        user_service = UserService(db)
        users, total = await user_service.get_users(skip=skip, limit=limit)
        # 确保每个用户对象都被正确序列化
        logger.info(f"Returned {len(users)} users to user {current_user.id}.")
        return [User.model_validate(user) for user in users], total

    @staticmethod
    @router.get("/users/{user_id}", response_model=User, dependencies=[Depends(require_permissions(["user:read"]))]) # 添加权限
    async def get_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(require_permissions(["user:read"]))
    ) -> UserModel:
        """获取用户详情"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) requesting detail for user {user_id}.")
        user_service = UserService(db)
        user = await user_service.get_by_id(user_id)
        if not user:
            logger.warning(f"User {user_id} not found for detail request by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"Returned detail for user {user_id} to user {current_user.id}.")
        return user

    @staticmethod
    @router.post("/add", response_model=User, dependencies=[Depends(require_permissions(["user:create"]))]) # 添加权限
    async def create_user(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(require_permissions(["user:create"]))
    ) -> UserModel:
        """创建用户"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to create user: {user_data.user_name}.")
        user_service = UserService(db)
        # 检查用户名是否已存在
        if await user_service.get_by_username(user_data.user_name):
            logger.warning(f"Attempted to create user with existing username {user_data.user_name} by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        new_user = await user_service.create(user_data, current_user.user_name)
        logger.info(f"User {new_user.id} ({new_user.user_name}) created by user {current_user.id}.")
        return new_user

    @staticmethod
    @router.put("/users/{user_id}", response_model=User, dependencies=[Depends(require_permissions(["user:update"]))]) # 添加权限
    async def update_user(
        user_id: int,
        user_data: UserUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(require_permissions(["user:update"]))
    ) -> UserModel:
        """更新用户"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to update user {user_id} with data: {user_data.dict()}")
        user_service = UserService(db)
        updated_user = await user_service.update(user_id, user_data, current_user.user_name)
        if not updated_user:
            logger.warning(f"User {user_id} not found for update by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"User {user_id} updated by user {current_user.id}.")
        return updated_user

    @staticmethod
    @router.delete("/users/{user_id}", response_model=bool, dependencies=[Depends(require_permissions(["user:delete"]))]) # 添加权限
    async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(require_permissions(["user:delete"]))
    ) -> bool:
        """删除用户"""
        logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to delete user {user_id}.")
        # 不允许删除自己
        if user_id == current_user.id:
            logger.warning(f"User {current_user.id} attempted to delete self.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete yourself"
            )
        
        user_service = UserService(db)
        if not await user_service.delete(user_id):
            logger.warning(f"User {user_id} not found for deletion by user {current_user.id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"User {user_id} deleted by user {current_user.id}.")
        return True 