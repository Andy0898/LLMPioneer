from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.conversation import ConversationModel
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

class ConversationService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: ConversationCreate) -> ConversationModel:
        logger.info(f"Creating new conversation for user {obj_in.user_id} with title: {obj_in.title}.")
        db_obj = ConversationModel(
            title=obj_in.title,
            user_id=obj_in.user_id,
            create_by=obj_in.create_by
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"Conversation {db_obj.id} created successfully for user {obj_in.user_id}.")
        return db_obj

    @staticmethod
    async def update(db: AsyncSession, db_obj: ConversationModel, obj_in: ConversationUpdate) -> ConversationModel:
        logger.info(f"Updating conversation {db_obj.id} for user {db_obj.user_id} with data: {obj_in.dict(exclude_unset=True)}.")
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"Conversation {db_obj.id} updated successfully.")
        return db_obj

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[ConversationModel]:
        logger.debug(f"Fetching conversation by ID: {id}.")
        result = await db.execute(
            select(ConversationModel).filter(ConversationModel.id == id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            logger.debug(f"Conversation {id} found.")
        else:
            logger.debug(f"Conversation {id} not found.")
        return conversation

    @staticmethod
    async def get_multi(
        db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ConversationModel]:
        logger.debug(f"Fetching multiple conversations for user {user_id}. Skip: {skip}, Limit: {limit}.")
        result = await db.execute(
            select(ConversationModel)
            .filter(ConversationModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        conversations = result.scalars().all()
        logger.debug(f"Returned {len(conversations)} conversations for user {user_id}.")
        return list(conversations)

    @staticmethod
    async def get_total(db: AsyncSession, user_id: int) -> int:
        logger.debug(f"Counting total conversations for user {user_id}.")
        result = await db.execute(
            select(ConversationModel)
            .filter(ConversationModel.user_id == user_id)
        )
        total = len(result.scalars().all())
        logger.debug(f"Total conversations for user {user_id}: {total}.")
        return total 

    @staticmethod
    async def delete(db: AsyncSession, id: int) -> bool:
        """
        Delete a conversation and its related messages (cascade delete).
        
        Args:
            db: Database session
            id: Conversation ID to delete
            
        Returns:
            Boolean indicating success
        """
        logger.info(f"Deleting conversation {id} and its messages.")
        conversation = await ConversationService.get(db=db, id=id)
        if not conversation:
            logger.warning(f"Conversation {id} not found for deletion.")
            return False
            
        # The cascade delete is handled at the database level via the relationship
        # defined in the ConversationModel (cascade="all, delete-orphan")
        await db.delete(conversation)
        await db.commit()
        logger.info(f"Conversation {id} and its messages deleted successfully.")
        return True 