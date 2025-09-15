from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1 import deps
from app.db.models.user import UserModel
from app.schemas.document_category import (
    DocumentCategoryCreate,
    DocumentCategoryUpdate,
    DocumentCategoryTree
)
from app.services.document_category_service import DocumentCategoryService
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

router = APIRouter()

@router.post("/knowledge/category/create", response_model=DocumentCategoryTree)
async def create_personal_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_in: DocumentCategoryCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentCategoryTree:
    """创建个人知识库分类"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to create personal category: {category_in.name}")
    category_in.type = 1  # 设置为个人知识库
    category = await DocumentCategoryService.create_category(
        db=db,
        obj_in=category_in,
        user_id=current_user.id
    )
    logger.info(f"Personal category {category.id} ({category.name}) created by user {current_user.id}.")
    return category

@router.get("/knowledge/category/list", response_model=List[DocumentCategoryTree])
async def get_personal_categories(
    db: AsyncSession = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[DocumentCategoryTree]:
    """获取个人知识库分类列表"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting personal category list.")
    categories = await DocumentCategoryService.get_category_tree(
        db=db,
        type=1,  # 个人知识库
        user_id=current_user.id
    )
    logger.info(f"Returned {len(categories)} personal categories to user {current_user.id}.")
    return categories

@router.put("/knowledge/category/{category_id}", response_model=DocumentCategoryTree)
async def update_personal_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int,
    category_in: DocumentCategoryUpdate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentCategoryTree:
    """更新个人知识库分类"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to update personal category {category_id} with data: {category_in.dict()}")
    category = await DocumentCategoryService.update_category(
        db=db,
        category_id=category_id,
        obj_in=category_in,
        user_id=current_user.id
    )
    if not category:
        logger.warning(f"Personal category {category_id} not found for update by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Category not found")
    logger.info(f"Personal category {category_id} updated by user {current_user.id}.")
    return category

@router.delete("/knowledge/category/{category_id}")
async def delete_personal_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> dict:
    """删除个人知识库分类"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to delete personal category {category_id}.")
    success = await DocumentCategoryService.delete_category(
        db=db,
        category_id=category_id,
        user_id=current_user.id
    )
    if not success:
        logger.warning(f"Personal category {category_id} not found for deletion by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Category not found")
    logger.info(f"Personal category {category_id} deleted by user {current_user.id}.")
    return {"status": "success"} 