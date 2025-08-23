from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.llm_configuration import LlmConfigurationModel
from app.schemas.llm_configuration import LlmConfigurationCreate, LlmConfigurationUpdate

class LlmConfigurationService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: LlmConfigurationCreate) -> LlmConfigurationModel:
        db_obj = LlmConfigurationModel(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update(
        db: AsyncSession, db_obj: LlmConfigurationModel, obj_in: LlmConfigurationUpdate
    ) -> LlmConfigurationModel:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[LlmConfigurationModel]:
        result = await db.execute(
            select(LlmConfigurationModel).filter(LlmConfigurationModel.id == id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_en_name(db: AsyncSession, llm_en_name: str) -> Optional[LlmConfigurationModel]:
        result = await db.execute(
            select(LlmConfigurationModel).filter(LlmConfigurationModel.llm_en_name == llm_en_name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_multi(
        db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[LlmConfigurationModel]:
        result = await db.execute(
            select(LlmConfigurationModel)
            .filter(LlmConfigurationModel.status == 1)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_total(db: AsyncSession) -> int:
        result = await db.execute(
            select(LlmConfigurationModel)
            .filter(LlmConfigurationModel.status == 1)
        )
        return len(result.scalars().all()) 