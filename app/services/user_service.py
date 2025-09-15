from typing import Optional, List, Tuple
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import UserModel, RoleModel, UserRoleModel
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info("UserService initialized.")

    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """
        通过用户名获取用户
        """
        logger.debug(f"Fetching user by username: {username}.")
        result = await self.db.execute(
            select(UserModel)
            .options(selectinload(UserModel.user_roles)) # 修正为 user_roles
            .where(UserModel.user_name == username)
        )
        user = result.scalar_one_or_none()
        if user:
            logger.debug(f"User {username} found.")
        else:
            logger.debug(f"User {username} not found.")
        return user

    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """
        通过ID获取用户
        """
        logger.debug(f"Fetching user by ID: {user_id}.")
        result = await self.db.execute(
            select(UserModel)
            .options(selectinload(UserModel.user_roles)) # 修正为 user_roles
            .where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            logger.debug(f"User {user_id} found.")
        else:
            logger.debug(f"User {user_id} not found.")
        return user

    async def create(self, user_data: UserCreate, operator: str) -> UserModel:
        """
        创建用户
        """
        logger.info(f"User {operator} attempting to create user: {user_data.user_name}.")
        db_user = UserModel(
            user_name=user_data.user_name,
            password=get_password_hash(user_data.password),
            # email=user_data.email,
            phone=user_data.phone,
            status=True,
            create_by=operator
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        logger.info(f"User {db_user.id} ({db_user.user_name}) created successfully by {operator}.")

        role_ids = user_data.role_ids
        if role_ids:
            logger.info(f"Assigning roles {role_ids} to new user {db_user.id}.")
            for role_id in role_ids:
                # 检查角色是否存在
                role = await self.db.scalar(select(RoleModel).where(RoleModel.id == role_id))
                if role:
                    user_role = UserRoleModel(user_id=db_user.id, role_id=role_id, create_by=operator)
                    self.db.add(user_role)
                    logger.debug(f"Role {role_id} assigned to user {db_user.id}.")
                else:
                    logger.warning(f"Role {role_id} not found when assigning to user {db_user.id}.")
            await self.db.commit()
            
            # 关键：在返回db_user之前，重新查询并预加载所有关联关系
            # 确保roles（通过association_proxy）能够被正确序列化
            result = await self.db.execute(
                select(UserModel)
                .options(selectinload(UserModel.user_roles).selectinload(UserRoleModel.role))
                .where(UserModel.id == db_user.id)
            )
            db_user = result.scalar_one_or_none()
            logger.info(f"Roles assigned and user {db_user.id} refreshed.")
            # await self.db.refresh(db_user) # 刷新用户以加载新关联的角色
        
        return db_user

    async def update(
        self, user_id: int, user_data: UserUpdate, operator: str
    ) -> Optional[UserModel]:
        """
        更新用户信息
        """
        logger.info(f"User {operator} attempting to update user {user_id} with data: {user_data.dict(exclude_unset=True)}.")
        db_user = await self.get_by_id(user_id)
        if not db_user:
            logger.warning(f"User {user_id} not found for update by {operator}.")
            return None
            
        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])
            logger.debug(f"Password updated for user {user_id}.")
            
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db_user.update_by = operator
        
        await self.db.commit()
        await self.db.refresh(db_user)
        logger.info(f"User {user_id} updated successfully by {operator}.")
        return db_user

    # async def authenticate(self, username: str, password: str) -> Optional[UserModel]:
    #     """
    #     用户认证
    #     """
    #     result = await self.db.execute(
    #         select(UserModel)
    #         .options(selectinload(UserModel.roles))
    #         .where(UserModel.user_name == username)
    #     )
    #     user = result.scalar_one_or_none()
    #     if not user:
    #         return None
    #     if not verify_password(password, user.password):
    #         # 更新登录错误次数
    #         user.error_num += 1
    #         if user.error_num >= 5:  # 5次错误后锁定账户
    #             user.is_locked = True
    #         await self.db.commit()
    #         return None
    #     # 登录成功，重置错误次数
    #     if user.error_num > 0:
    #         user.error_num = 0
    #         await self.db.commit()
    #     return user

    async def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """
        修改密码
        """
        logger.info(f"Attempting to change password for user ID: {user_id}.")
        user = await self.get_by_id(user_id)
        if not user:
            logger.warning(f"Password change failed for user ID {user_id}: User not found.")
            return False
        if not verify_password(old_password, user.password):
            logger.warning(f"Password change failed for user ID {user_id}: Old password mismatch.")
            return False
        
        user.password = get_password_hash(new_password)
        await self.db.commit()
        logger.info(f"Password successfully changed for user ID: {user_id}.")
        return True

    async def get_users(self, skip: int = 0, limit: int = 10) -> Tuple[List[UserModel], int]:
        """
        获取用户列表
        """
        logger.debug(f"Fetching user list. Skip: {skip}, Limit: {limit}.")
        query = select(UserModel).options(selectinload(UserModel.user_roles))
        total = await self.db.scalar(
            select(func.count()).select_from(UserModel)
        )
        
        result = await self.db.execute(
            query.offset(skip).limit(limit)
        )
        users = result.scalars().all()
        logger.debug(f"Returned {len(users)} users (total: {total}).")
        return users, total

    async def delete(self, user_id: int) -> bool:
        """
        删除用户
        """
        logger.info(f"Attempting to delete user ID: {user_id}.")
        db_user = await self.get_by_id(user_id)
        if not db_user:
            logger.warning(f"User {user_id} not found for deletion.")
            return False
        await self.db.delete(db_user)
        await self.db.commit()
        logger.info(f"User {user_id} deleted successfully.")
        return True