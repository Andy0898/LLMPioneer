from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.conversation import ConversationModel
from app.schemas.conversation import ConversationCreate, ConversationUpdate

class ConversationService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: ConversationCreate) -> ConversationModel:
        db_obj = ConversationModel(
            title=obj_in.title,
            user_id=obj_in.user_id,
            create_by=obj_in.create_by
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update(db: AsyncSession, db_obj: ConversationModel, obj_in: ConversationUpdate) -> ConversationModel:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[ConversationModel]:
        result = await db.execute(
            select(ConversationModel).filter(ConversationModel.id == id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_multi(
        db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ConversationModel]:
        result = await db.execute(
            select(ConversationModel)
            .filter(ConversationModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_total(db: AsyncSession, user_id: int) -> int:
        result = await db.execute(
            select(ConversationModel)
            .filter(ConversationModel.user_id == user_id)
        )
        return len(result.scalars().all()) 