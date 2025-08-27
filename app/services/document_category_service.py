from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.document_category import DocumentCategory
from app.schemas.document_category import DocumentCategoryCreate, DocumentCategoryUpdate
from app.config.logger import get_logger # 导入日志

logger = get_logger(__name__) # 获取Logger实例

class DocumentCategoryService:
    @staticmethod
    async def create_category(db: AsyncSession, obj_in: DocumentCategoryCreate, user_id: int) -> DocumentCategory:
        logger.info(f"Creating new document category for user {user_id} with name: {obj_in.name}, type: {obj_in.type}.")
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
        logger.info(f"Document category {db_obj.id} ({db_obj.name}) created successfully by user {user_id}.")
        return db_obj

    @staticmethod
    async def get_category_tree(db: AsyncSession, type: int = 0, user_id: int = 0) -> List[DocumentCategory]:
        logger.debug(f"Fetching category tree. Type: {type}, User ID: {user_id}.")
        filters = [DocumentCategory.is_deleted == 0]
        if type == 1:  # 个人知识库
            filters.append(DocumentCategory.user_id == user_id)
            logger.debug(f"Filtering personal knowledge base categories for user {user_id}.")
        else:  # 企业知识库
            filters.append(DocumentCategory.type == 0)
            logger.debug("Filtering enterprise knowledge base categories.")
        
        stmt = select(DocumentCategory).filter(
            and_(*filters)
        ).order_by(DocumentCategory.sort_no.asc())
        
        result = await db.execute(stmt)
        categories = result.scalars().all()
        
        tree = DocumentCategoryService.build_tree(categories)
        logger.debug(f"Built category tree with {len(tree)} top-level items.")
        return tree

    @staticmethod
    def build_tree(categories: List[DocumentCategory], parent_id: int = 0) -> List[dict]:
        """构建树形结构"""
        logger.debug(f"Building tree for parent_id: {parent_id}.")
        tree = []
        for category in categories:
            if category.parent_id == parent_id:
                children = DocumentCategoryService.build_tree(categories, category.id)
                category_dict = category.__dict__.copy() # 使用copy避免修改原始对象
                if children:
                    category_dict['children'] = children
                tree.append(category_dict)
        logger.debug(f"Tree built for parent_id {parent_id} with {len(tree)} items.")
        return tree

    @staticmethod
    async def update_category(
        db: AsyncSession, 
        category_id: int, 
        obj_in: DocumentCategoryUpdate,
        user_id: int
    ) -> Optional[DocumentCategory]:
        logger.info(f"Updating document category {category_id} by user {user_id} with data: {obj_in.dict(exclude_unset=True)}.")
        stmt = select(DocumentCategory).filter(
            DocumentCategory.id == category_id,
            DocumentCategory.is_deleted == 0
        )
        result = await db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            logger.warning(f"Document category {category_id} not found for update by user {user_id}.")
            return None
            
        update_data = obj_in.dict(exclude_unset=True)
        update_data['update_by'] = str(user_id)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"Document category {category_id} updated successfully by user {user_id}.")
        return db_obj

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int, user_id: int) -> bool:
        logger.info(f"Attempting to delete document category {category_id} by user {user_id}.")
        stmt = select(DocumentCategory).filter(
            DocumentCategory.id == category_id,
            DocumentCategory.is_deleted == 0
        )
        result = await db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            logger.warning(f"Document category {category_id} not found for deletion by user {user_id}.")
            return False
            
        db_obj.is_deleted = 1
        db_obj.update_by = str(user_id)
        
        await db.commit()
        logger.info(f"Document category {category_id} soft-deleted successfully by user {user_id}.")
        return True
    
    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: int) -> Optional[DocumentCategory]:
        logger.debug(f"Fetching document category by ID: {category_id}.")
        stmt = select(DocumentCategory).filter(
            DocumentCategory.id == category_id,
            DocumentCategory.is_deleted == 0
        )
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()
        if category:
            logger.debug(f"Document category {category_id} found.")
        else:
            logger.debug(f"Document category {category_id} not found.")
        return category