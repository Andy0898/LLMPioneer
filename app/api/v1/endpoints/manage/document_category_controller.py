from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import UserModel
from app.api.v1 import deps
from app.schemas.document_category import (
    DocumentCategoryCreate,
    DocumentCategoryUpdate,
    DocumentCategoryTree
)
from app.services.document_category_service import DocumentCategoryService
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

router = APIRouter()

@router.post("/category/create", response_model=DocumentCategoryTree)
async def create_enterprise_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_in: DocumentCategoryCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentCategoryTree:
    """创建企业知识库分类"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to create category: {category_in.name}")
    category = await DocumentCategoryService.create_category(
        db=db,
        obj_in=category_in,
        user_id=current_user.id
    )
    logger.info(f"Category {category.id} ({category.name}) created by user {current_user.id}.")
    return category

@router.get("/category/list", response_model=List[DocumentCategoryTree])
async def get_enterprise_categories(
    db: AsyncSession = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[DocumentCategoryTree]:
    """获取企业知识库分类列表"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting category list.")
    categories = await DocumentCategoryService.get_category_tree(
        db=db,
        type=0  # 企业知识库
    )
    logger.info(f"Returned {len(categories)} categories to user {current_user.id}.")
    return categories

@router.put("/category/{category_id}", response_model=DocumentCategoryTree)
async def update_enterprise_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int,
    category_in: DocumentCategoryUpdate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentCategoryTree:
    """更新企业知识库分类"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to update category {category_id} with data: {category_in.dict()}")
    category = await DocumentCategoryService.update_category(
        db=db,
        category_id=category_id,
        obj_in=category_in,
        user_id=current_user.id
    )
    if not category:
        logger.warning(f"Category {category_id} not found for update by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Category not found")
    logger.info(f"Category {category_id} updated by user {current_user.id}.")
    return category

@router.delete("/category/{category_id}")
async def delete_enterprise_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> dict:
    """删除企业知识库分类"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to delete category {category_id}.")
    success = await DocumentCategoryService.delete_category(
        db=db,
        category_id=category_id,
        user_id=current_user.id
    )
    if not success:
        logger.warning(f"Category {category_id} not found for deletion by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Category not found")
    logger.info(f"Category {category_id} deleted by user {current_user.id}.")
    return {"status": "success"}

@router.get("/category/{category_id}", response_model=DocumentCategoryTree)
async def get_enterprise_category_detail(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentCategoryTree:
    """根据ID获取企业知识库分类详情"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting detail for category {category_id}.")
    category = await DocumentCategoryService.get_category_by_id(db=db, category_id=category_id)
    if not category:
        logger.warning(f"Category {category_id} not found for detail request by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Category not found")
    
    logger.info(f"Returned detail for category {category_id} to user {current_user.id}.")
    return category