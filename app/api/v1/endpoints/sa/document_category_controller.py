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

router = APIRouter()

@router.post("/knowledge/category/create", response_model=DocumentCategoryTree)
async def create_personal_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_in: DocumentCategoryCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentCategoryTree:
    """创建个人知识库分类"""
    category_in.type = 1  # 设置为个人知识库
    category = await DocumentCategoryService.create_category(
        db=db,
        obj_in=category_in,
        user_id=current_user.id
    )
    return category

@router.get("/knowledge/category/list", response_model=List[DocumentCategoryTree])
async def get_personal_categories(
    db: AsyncSession = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[DocumentCategoryTree]:
    """获取个人知识库分类列表"""
    categories = await DocumentCategoryService.get_category_tree(
        db=db,
        type=1,  # 个人知识库
        user_id=current_user.id
    )
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
    category = await DocumentCategoryService.update_category(
        db=db,
        category_id=category_id,
        obj_in=category_in,
        user_id=current_user.id
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/knowledge/category/{category_id}")
async def delete_personal_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> dict:
    """删除个人知识库分类"""
    success = await DocumentCategoryService.delete_category(
        db=db,
        category_id=category_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "success"} 