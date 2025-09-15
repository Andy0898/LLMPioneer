from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.llm_configuration import LlmConfigurationModel
from app.schemas.llm_configuration import LlmConfigurationCreate, LlmConfigurationUpdate
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

class LlmConfigurationService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: LlmConfigurationCreate) -> LlmConfigurationModel:
        logger.info(f"Creating new LLM configuration: {obj_in.llm_name} ({obj_in.llm_en_name}).")
        db_obj = LlmConfigurationModel(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"LLM configuration {db_obj.id} ({db_obj.llm_name}) created successfully.")
        return db_obj

    @staticmethod
    async def update(
        db: AsyncSession, db_obj: LlmConfigurationModel, obj_in: LlmConfigurationUpdate
    ) -> LlmConfigurationModel:
        logger.info(f"Updating LLM configuration {db_obj.id} with data: {obj_in.dict(exclude_unset=True)}.")
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"LLM configuration {db_obj.id} updated successfully.")
        return db_obj

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[LlmConfigurationModel]:
        logger.debug(f"Fetching LLM configuration by ID: {id}.")
        result = await db.execute(
            select(LlmConfigurationModel).filter(LlmConfigurationModel.id == id)
        )
        llm_config = result.scalar_one_or_none()
        if llm_config:
            logger.debug(f"LLM configuration {id} found.")
        else:
            logger.debug(f"LLM configuration {id} not found.")
        return llm_config

    @staticmethod
    async def get_by_en_name(db: AsyncSession, llm_en_name: str) -> Optional[LlmConfigurationModel]:
        logger.debug(f"Fetching LLM configuration by English name: {llm_en_name}.")
        result = await db.execute(
            select(LlmConfigurationModel).filter(LlmConfigurationModel.llm_en_name == llm_en_name)
        )
        llm_config = result.scalar_one_or_none()
        if llm_config:
            logger.debug(f"LLM configuration with name {llm_en_name} found.")
        else:
            logger.debug(f"LLM configuration with name {llm_en_name} not found.")
        return llm_config

    @staticmethod
    async def get_multi(
        db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[LlmConfigurationModel]:
        logger.debug(f"Fetching multiple LLM configurations. Skip: {skip}, Limit: {limit}.")
        result = await db.execute(
            select(LlmConfigurationModel)
            .filter(LlmConfigurationModel.status == 1)
            .offset(skip)
            .limit(limit)
        )
        llm_configs = result.scalars().all()
        logger.debug(f"Returned {len(llm_configs)} LLM configurations.")
        return llm_configs

    @staticmethod
    async def get_total(db: AsyncSession) -> int:
        logger.debug("Counting total active LLM configurations.")
        result = await db.execute(
            select(LlmConfigurationModel)
            .filter(LlmConfigurationModel.status == 1)
        )
        total = len(result.scalars().all())
        logger.debug(f"Total active LLM configurations: {total}.")
        return total 