from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession  # 修改这里
from app.api.v1.deps import get_db, get_current_active_user, require_permissions # 导入 require_permissions
from app.db.models.user import UserModel
from app.schemas.llm_configuration import (
    LlmConfigurationCreate,
    LlmConfigurationResponse,
    LlmConfigurationUpdate
)
from app.services.llm_configuration_service import LlmConfigurationService
# from app.core.config import CONFIG as settings
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

router = APIRouter()

@router.get("/llm/list", response_model=List[LlmConfigurationResponse], dependencies=[Depends(require_permissions(["llm:list"]))]) # 添加权限
async def get_llm_list(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取可用的LLM列表"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting LLM configuration list. Skip: {skip}, Limit: {limit}.")
    llm_configs = await LlmConfigurationService.get_multi(db=db, skip=skip, limit=limit)
    logger.info(f"Returned {len(llm_configs)} LLM configurations to user {current_user.id}.")
    return llm_configs

@router.post("/llm", response_model=LlmConfigurationResponse, dependencies=[Depends(require_permissions(["llm:create"]))]) # 添加权限
async def create_llm_config(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    llm_config_in: LlmConfigurationCreate
):
    """创建新的LLM配置"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to create LLM configuration: {llm_config_in.llm_name} ({llm_config_in.llm_en_name}).")
    # 检查是否有管理员权限
    # if not current_user.get("is_admin"):
    #     logger.warning(f"User {current_user.id} attempted to create LLM config without admin permissions.")
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # 检查英文名是否已存在
    existing_config = await LlmConfigurationService.get_by_en_name(
        db=db, llm_en_name=llm_config_in.llm_en_name
    )
    if existing_config:
        logger.warning(f"Attempted to create LLM config with existing English name {llm_config_in.llm_en_name} by user {current_user.id}.")
        raise HTTPException(status_code=400, detail="LLM configuration with this name already exists")
    
    llm_config_in.create_by = current_user.user_name # 修正为 current_user.user_name
    llm_config = await LlmConfigurationService.create(db=db, obj_in=llm_config_in)
    logger.info(f"LLM configuration {llm_config.id} ({llm_config.llm_name}) created by user {current_user.id}.")
    return llm_config

@router.put("/llm/{llm_id}", response_model=LlmConfigurationResponse, dependencies=[Depends(require_permissions(["llm:update"]))]) # 添加权限
async def update_llm_config(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    llm_id: int,
    llm_config_in: LlmConfigurationUpdate
):
    """更新LLM配置"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to update LLM configuration {llm_id} with data: {llm_config_in.dict()}")
    # 检查是否有管理员权限
    # if not current_user.get("is_admin"):
    #     logger.warning(f"User {current_user.id} attempted to update LLM config {llm_id} without admin permissions.")
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    
    llm_config = await LlmConfigurationService.get(db=db, id=llm_id)
    if not llm_config:
        logger.warning(f"LLM configuration {llm_id} not found for update by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="LLM configuration not found")
    
    # 如果更新了英文名，检查是否与其他配置冲突
    if llm_config_in.llm_en_name and llm_config_in.llm_en_name != llm_config.llm_en_name:
        existing_config = await LlmConfigurationService.get_by_en_name(
            db=db, llm_en_name=llm_config_in.llm_en_name
        )
        if existing_config:
            logger.warning(f"Attempted to update LLM config {llm_id} to existing English name {llm_config_in.llm_en_name} by user {current_user.id}.")
            raise HTTPException(
                status_code=400,
                detail="LLM configuration with this name already exists"
            )
    
    llm_config_in.update_by = current_user.user_name # 修正为 current_user.user_name
    llm_config = await LlmConfigurationService.update(
        db=db, db_obj=llm_config, obj_in=llm_config_in
    )
    logger.info(f"LLM configuration {llm_id} updated by user {current_user.id}.")
    return llm_config