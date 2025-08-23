from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.document_category import DocumentCategory
from app.schemas.document_category import DocumentCategoryCreate, DocumentCategoryUpdate

class DocumentCategoryService:
    @staticmethod
    async def create_category(db: AsyncSession, obj_in: DocumentCategoryCreate, user_id: int) -> DocumentCategory:
        db_obj = DocumentCategory(
            code=obj_in.code,
            name=obj_in.name,
            description=obj_in.description,
            parent_id=obj_in.parent_id,
            user_id=user_id,
            type=obj_in.type,
            status=1,
            sort_no=obj_in.sort_no,
            create_by=str(user_id)
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get_category_tree(db: AsyncSession, type: int = 0, user_id: int = 0) -> List[DocumentCategory]:
        """获取分类树形结构"""
        filters = [DocumentCategory.is_deleted == 0]
        if type == 1:  # 个人知识库
            filters.append(DocumentCategory.user_id == user_id)
        else:  # 企业知识库
            filters.append(DocumentCategory.type == 0)
        
        stmt = select(DocumentCategory).filter(
            and_(*filters)
        ).order_by(DocumentCategory.sort_no.asc())
        
        result = await db.execute(stmt)
        categories = result.scalars().all()
        
        return DocumentCategoryService.build_tree(categories)

    @staticmethod
    def build_tree(categories: List[DocumentCategory], parent_id: int = 0) -> List[dict]:
        """构建树形结构"""
        tree = []
        for category in categories:
            if category.parent_id == parent_id:
                children = DocumentCategoryService.build_tree(categories, category.id)
                if children:
                    category_dict = category.__dict__
                    category_dict['children'] = children
                    tree.append(category_dict)
                else:
                    tree.append(category.__dict__)
        return tree

    @staticmethod
    async def update_category(
        db: AsyncSession, 
        category_id: int, 
        obj_in: DocumentCategoryUpdate,
        user_id: int
    ) -> Optional[DocumentCategory]:
        stmt = select(DocumentCategory).filter(
            DocumentCategory.id == category_id,
            DocumentCategory.is_deleted == 0
        )
        result = await db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            return None
            
        update_data = obj_in.dict(exclude_unset=True)
        update_data['update_by'] = str(user_id)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int, user_id: int) -> bool:
        stmt = select(DocumentCategory).filter(
            DocumentCategory.id == category_id,
            DocumentCategory.is_deleted == 0
        )
        result = await db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            return False
            
        db_obj.is_deleted = 1
        db_obj.update_by = str(user_id)
        
        await db.commit()
        return True