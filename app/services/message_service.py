from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.message import MessageModel
from app.schemas.message import MessageCreate, MessageUpdate

class MessageService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: MessageCreate) -> MessageModel:
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
        return db_obj

    @staticmethod
    async def update(db: AsyncSession, db_obj: MessageModel, obj_in: MessageUpdate) -> MessageModel:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[MessageModel]:
        result = await db.execute(
            select(MessageModel).filter(MessageModel.id == id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_conversation(
        db: AsyncSession, conversation_id: int, skip: int = 0, limit: int = 100
    ) -> List[MessageModel]:
        result = await db.execute(
            select(MessageModel)
            .filter(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.create_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_conversation_messages_count(db: AsyncSession, conversation_id: int) -> int:
        result = await db.execute(
            select(MessageModel)
            .filter(MessageModel.conversation_id == conversation_id)
        )
        return len(result.scalars().all()) 