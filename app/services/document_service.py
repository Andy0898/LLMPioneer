from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
import os
from datetime import datetime
from app.db.models.document_info import DocumentInfo
from app.db.models.document_settings import DocumentSettings
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentSettingsCreate
from config.settings import settings
from app.core.rag.document_processor import DocumentProcessor
from app.core.rag.document_splitter import ChunkConfig

from config.logger import get_logger
logger = get_logger(__name__)

class DocumentService:
    @staticmethod
    async def create_document(
        db: AsyncSession,
        file: UploadFile,
        category_id: int,
        user_id: int
        # description: str = None
    ) -> DocumentInfo:
        # 生成文件存储路径
        file_dir = os.path.join(settings.UPLOAD_DIR, datetime.now().strftime("%Y%m"))
        os.makedirs(file_dir, exist_ok=True)
        
        # 生成文件名
        file_ext = os.path.splitext(file.filename)[1]
        new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}{file_ext}"
        file_path = os.path.join(file_dir, new_filename)
        
        # 保存文件
        with open(file_path, "wb+") as file_object:
            file_object.write(await file.read())
        
        # 创建文档记录
        db_obj = DocumentInfo(
            file_name=file.filename,
            category_id=category_id,
            file_url=file_path,
            status=0,  # 初始状态
            create_by=str(user_id)
            # description=description
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    async def get_by_id(db: AsyncSession, document_id: int) -> Optional[DocumentInfo]:
        """
        通过ID获取文档
        """
        return await db.get(DocumentInfo, document_id)
    
    @staticmethod
    async def get_document_list(
        db: AsyncSession,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[DocumentInfo]:
        filters = [DocumentInfo.is_deleted == 0]
        
        if category_id:
            filters.append(DocumentInfo.category_id == category_id)
            
        if user_id:
            filters.append(DocumentInfo.create_by == str(user_id))
        
        stmt = select(DocumentInfo).filter(
            and_(*filters)
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def delete_document(db: AsyncSession, document_id: int, user_id: int) -> bool:
        stmt = select(DocumentInfo).filter(
            DocumentInfo.id == document_id,
            DocumentInfo.is_deleted == 0
        )
        result = await db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            return False
            
        db_obj.is_deleted = 1
        db_obj.update_by = str(user_id)
        
        await db.commit()
        return True

    @staticmethod
    async def create_document_settings(
        db: AsyncSession,
        document_id: int,
        settings_in: DocumentSettingsCreate,
        user_id: int
    ) -> DocumentSettings:
        db_obj = DocumentSettings(
            document_id=document_id,
            parse_level=settings_in.parse_level,
            chunking_type=settings_in.chunking_type,
            chunk_identifier=settings_in.chunk_identifier,
            maximum_length=settings_in.maximum_length,
            chunking_overlap=settings_in.chunking_overlap,
            create_by=settings_in.create_by
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get_document_settings(
        db: AsyncSession,
        document_id: int
    ) -> Optional[DocumentSettings]:
        stmt = select(DocumentSettings).filter(
            DocumentSettings.document_id == document_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_document_settings(
        db: AsyncSession,
        document_id: int,
        settings_in: DocumentSettingsCreate,
        user_id: int
    ) -> Optional[DocumentSettings]:
        db_obj = await DocumentService.get_document_settings(db, document_id)
        
        if not db_obj:
            return await DocumentService.create_document_settings(db, document_id, settings_in, user_id)
            
        update_data = settings_in.dict(exclude_unset=True)
        update_data['update_by'] = str(user_id)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    async def process_document(
        db: AsyncSession,
        document_id: int,
    ) -> Dict[str, Any]:
        """处理文档并构建知识库"""
        try:
            # 1. 获取文档信息
            stmt = select(DocumentInfo).filter(
                DocumentInfo.id == document_id,
                DocumentInfo.is_deleted == 0
            )
            result = await db.execute(stmt)
            document = result.scalar_one_or_none()
            
            if not document:
                raise ValueError(f"文档不存在: {document_id}")

            # 2. 获取文档设置
            document_settings = await DocumentService.get_document_settings(db, document_id)
            if not document_settings:
                raise ValueError(f"文档设置未找到: {document_id}")

            # 3. 构建分块配置
            chunk_config = {
                "mode": document_settings.chunking_type,  # hierarchical, custom, auto
                "max_size": document_settings.maximum_length,
                "overlap_ratio": document_settings.chunking_overlap,
                "separators": document_settings.chunk_identifier.split(",") if document_settings.chunk_identifier else None
            }

            # 4. 创建文档处理器
            processor = DocumentProcessor(
                embedding_model="text2vec-base"  # 可以从配置中读取
            )

            # 5. 处理文档
            # 根据文档创建者判断是部门文档还是个人文档
            kb_type = "department" if document.category_id else "personal"
            owner_id = document.category_id if kb_type == "department" else document.create_by

            result = await processor.process(
                file_path=document.file_url,
                kb_type=kb_type,
                owner_id=owner_id,
                document_id=document_id,
                chunk_config=chunk_config
            )

            # 6. 更新文档状态
            document.status = 1  # 处理完成
            await db.commit()

            logger.info(f"文档处理完成: {document_id}")
            return result

        except Exception as e:
            logger.error(f"处理文档失败: {str(e)}")
            # 更新文档状态为处理失败
            if document:
                document.status = 2  # 处理失败
                await db.commit()
            raise

    @staticmethod
    async def get_document_chunks(
        db: AsyncSession,
        document_id: int,
        query: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """获取文档的分块列表，支持相似度搜索"""
        try:
            # 1. 获取文档信息
            stmt = select(DocumentInfo).filter(
                DocumentInfo.id == document_id,
                DocumentInfo.is_deleted == 0
            )
            result = await db.execute(stmt)
            document = result.scalar_one_or_none()
            
            if not document:
                raise ValueError(f"文档不存在: {document_id}")

            # 2. 确定知识库类型和所有者ID
            kb_type = "department" if document.category_id else "personal"
            owner_id = document.category_id if kb_type == "department" else document.create_by

            # 3. 创建文档处理器
            processor = DocumentProcessor(
                embedding_model="text2vec-base"  # 可以从配置中读取
            )

            # 4. 如果提供了查询，执行相似度搜索
            if query:
                chunks = await processor.search(
                    kb_type=kb_type,
                    owner_id=owner_id,
                    query=query,
                    top_k=top_k
                )
                
                # 过滤出属于当前文档的分块
                chunks = [
                    chunk for chunk in chunks 
                    if chunk.get("document_id") == document_id
                ]
            else:
                # 如果没有查询，直接返回文档的所有分块
                # 这里需要添加一个新的方法到 MilvusClient 中
                chunks = await processor.milvus_client.get_document_chunks(
                    collection_name=f"{kb_type}_kb",
                    document_id=document_id
                )

            return chunks

        except Exception as e:
            logger.error(f"获取文档分块失败: {str(e)}")
            raise

    @staticmethod
    async def search_similar_chunks(
        db: AsyncSession,
        document_id: int,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """搜索文档中相似的内容"""
        return await DocumentService.get_document_chunks(
            db=db,
            document_id=document_id,
            query=query,
            top_k=top_k
        )
       