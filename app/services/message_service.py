from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.db.models.message import MessageModel
from app.schemas.message import MessageCreate, MessageUpdate
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

class MessageService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: MessageCreate) -> MessageModel:
        logger.info(f"Creating new message for conversation {obj_in.conversation_id} by user {obj_in.create_by}. Question: {obj_in.question[:50]}...")
        db_obj = MessageModel(
            conversation_id=obj_in.conversation_id,
            llm_id=obj_in.llm_id,
            question=obj_in.question,
            content=obj_in.content,
            reasoning_content=obj_in.reasoning_content,
            create_by=obj_in.create_by
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"Message {db_obj.id} created successfully for conversation {obj_in.conversation_id}.")
        return db_obj

    @staticmethod
    async def update(db: AsyncSession, db_obj: MessageModel, obj_in: MessageUpdate) -> MessageModel:
        logger.info(f"Updating message {db_obj.id} for conversation {db_obj.conversation_id} with data: {obj_in.dict(exclude_unset=True)}.")
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"Message {db_obj.id} updated successfully.")
        return db_obj

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[MessageModel]:
        logger.debug(f"Fetching message by ID: {id}.")
        result = await db.execute(
            select(MessageModel).filter(MessageModel.id == id)
        )
        message = result.scalar_one_or_none()
        if message:
            logger.debug(f"Message {id} found.")
        else:
            logger.debug(f"Message {id} not found.")
        return message

    @staticmethod
    async def get_by_conversation(
        db: AsyncSession, conversation_id: int, skip: int = 0, limit: int = 100
    ) -> List[MessageModel]:
        logger.debug(f"Fetching messages for conversation {conversation_id}. Skip: {skip}, Limit: {limit}.")
        result = await db.execute(
            select(MessageModel)
            .filter(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.create_time.desc())
            .offset(skip)
            .limit(limit)
        )
        messages = result.scalars().all()
        logger.debug(f"Returned {len(messages)} messages for conversation {conversation_id}.")
        return list(messages)

    @staticmethod
    async def get_conversation_messages_count(db: AsyncSession, conversation_id: int) -> int:
        logger.debug(f"Counting messages for conversation {conversation_id}.")
        result = await db.execute(
            select(MessageModel)
            .filter(MessageModel.conversation_id == conversation_id)
        )
        total = len(result.scalars().all())
        logger.debug(f"Total messages for conversation {conversation_id}: {total}.")
        return total 

    @staticmethod
    async def delete(db: AsyncSession, id: int) -> bool:
        """
        Delete a message.
        
        Args:
            db: Database session
            id: Message ID to delete
            
        Returns:
            Boolean indicating success
        """
        logger.info(f"Deleting message {id}.")
        message = await MessageService.get(db=db, id=id)
        if not message:
            logger.warning(f"Message {id} not found for deletion.")
            return False
            
        await db.delete(message)
        await db.commit()
        logger.info(f"Message {id} deleted successfully.")
        return True

    @staticmethod
    async def get_messages_before_time(db: AsyncSession, conversation_id: int, before_time: datetime) -> List[MessageModel]:
        """
        Get messages in a conversation created before a specific time.
        
        Args:
            db: Database session
            conversation_id: ID of the conversation
            before_time: Get messages created before this time
            
        Returns:
            List of messages ordered by creation time (oldest first)
        """
        logger.debug(f"Fetching messages for conversation {conversation_id} created before {before_time}.")
        result = await db.execute(
            select(MessageModel)
            .filter(MessageModel.conversation_id == conversation_id)
            .filter(MessageModel.create_time < before_time)
            .order_by(MessageModel.create_time.asc())
        )
        messages = result.scalars().all()
        logger.debug(f"Returned {len(messages)} messages for conversation {conversation_id} before {before_time}.")
        return list(messages) 