from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile
import os
from datetime import datetime
from app.core.langchain.rag_pipeline import RAGPipeline
from app.db.models.document_info import DocumentInfo
from app.db.models.document_settings import DocumentSettings
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentSettingsCreate
from app.core.config import CONFIG as settings
from app.core.rag.document_processor import DocumentProcessor
from app.core.rag.document_splitter import ChunkConfig

from app.core.logger.logging_config_helper import get_configured_logger
logger = get_configured_logger("pioneer_handler")

class DocumentService:
    @staticmethod
    async def create_document(
        db: AsyncSession,
        file: UploadFile,
        category_id: int,
        user_id: int
        # description: str = None
    ) -> DocumentInfo:
        logger.info(f"User {user_id} attempting to create document: {file.filename} in category {category_id}.")
        # 生成文件存储路径
        file_dir = os.path.join(settings.upload.dir, datetime.now().strftime("%Y%m"))
        os.makedirs(file_dir, exist_ok=True)
        logger.debug(f"File directory created/ensured: {file_dir}.")
        
        # 生成文件名
        file_ext = os.path.splitext(file.filename)[1]
        new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}{file_ext}"
        file_path = os.path.join(file_dir, new_filename)
        logger.debug(f"New file path: {file_path}.")
        
        # 保存文件
        try:
            with open(file_path, "wb+") as file_object:
                file_object.write(await file.read())
            logger.info(f"File {file.filename} saved to {file_path}.")
        except Exception as e:
            logger.error(f"Failed to save file {file.filename} for user {user_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to save file: {file.filename}")
        
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
        logger.info(f"Document record {db_obj.id} created successfully for user {user_id}.")
        return db_obj
    
    @staticmethod
    async def get_by_id(db: AsyncSession, document_id: int) -> Optional[DocumentInfo]:
        """
        通过ID获取文档
        """
        logger.debug(f"Fetching document by ID: {document_id}.")
        document = await db.get(DocumentInfo, document_id)
        if document:
            logger.debug(f"Document {document_id} found.")
        else:
            logger.debug(f"Document {document_id} not found.")
        return document
    
    @staticmethod
    async def get_document_list(
        db: AsyncSession,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[DocumentInfo]:
        logger.debug(f"Fetching document list. Category: {category_id}, User: {user_id}, Skip: {skip}, Limit: {limit}.")
        filters = [DocumentInfo.is_deleted == 0]
        
        if category_id:
            filters.append(DocumentInfo.category_id == category_id)
            
        if user_id:
            filters.append(DocumentInfo.create_by == str(user_id))
        
        stmt = select(DocumentInfo).filter(
            and_(*filters)
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        documents = result.scalars().all()
        logger.debug(f"Returned {len(documents)} documents.")
        return documents

    @staticmethod
    async def delete_document(db: AsyncSession, document_id: int, user_id: int) -> bool:
        logger.info(f"User {user_id} attempting to soft-delete document {document_id}.")
        stmt = select(DocumentInfo).filter(
            DocumentInfo.id == document_id,
            DocumentInfo.is_deleted == 0
        )
        result = await db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        
        if not db_obj:
            logger.warning(f"Document {document_id} not found for soft-deletion by user {user_id}.")
            return False
            
        db_obj.is_deleted = 1
        db_obj.update_by = str(user_id)
        
        await db.commit()
        logger.info(f"Document {document_id} soft-deleted successfully by user {user_id}.")
        return True

    @staticmethod
    async def create_document_settings(
        db: AsyncSession,
        document_id: int,
        settings_in: DocumentSettingsCreate,
        user_id: int
    ) -> DocumentSettings:
        logger.info(f"User {user_id} attempting to create settings for document {document_id}.")
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
        logger.info(f"Settings for document {document_id} created successfully by user {user_id}.")
        return db_obj

    @staticmethod
    async def get_document_settings(
        db: AsyncSession,
        document_id: int
    ) -> Optional[DocumentSettings]:
        logger.debug(f"Fetching settings for document ID: {document_id}.")
        stmt = select(DocumentSettings).filter(
            DocumentSettings.document_id == document_id
        )
        result = await db.execute(stmt)
        settings = result.scalar_one_or_none()
        if settings:
            logger.debug(f"Settings for document {document_id} found.")
        else:
            logger.debug(f"Settings for document {document_id} not found.")
        return settings

    @staticmethod
    async def update_document_settings(
        db: AsyncSession,
        document_id: int,
        settings_in: DocumentSettingsCreate,
        user_id: int
    ) -> Optional[DocumentSettings]:
        logger.info(f"User {user_id} attempting to update settings for document {document_id} with data: {settings_in.dict(exclude_unset=True)}.")
        db_obj = await DocumentService.get_document_settings(db, document_id)
        
        if not db_obj:
            logger.warning(f"Settings for document {document_id} not found for update by user {user_id}. Attempting to create instead.")
            return await DocumentService.create_document_settings(db, document_id, settings_in, user_id)
            
        update_data = settings_in.dict(exclude_unset=True)
        update_data['update_by'] = str(user_id)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"Settings for document {document_id} updated successfully by user {user_id}.")
        return db_obj
    
    @staticmethod
    async def process_document(
        db: AsyncSession,
        document_id: int,
    ) -> Dict[str, Any]:
        """处理文档并构建知识库"""
        logger.info(f"Starting document processing for document ID: {document_id}.")
        document = None
        try:
            # 1. 获取文档信息
            stmt = select(DocumentInfo).filter(
                DocumentInfo.id == document_id,
                DocumentInfo.is_deleted == 0
            )
            result = await db.execute(stmt)
            document = result.scalar_one_or_none()
            
            if not document:
                logger.error(f"Document {document_id} not found or already deleted during processing.")
                raise ValueError(f"文档不存在: {document_id}")

            # 2. 获取文档设置
            document_settings = await DocumentService.get_document_settings(db, document_id)
            if not document_settings:
                logger.error(f"Document settings not found for document {document_id} during processing.")
                raise ValueError(f"文档设置未找到: {document_id}")

            # 3. 构建分块配置
            # 假设 overlap 是以整数百分比形式存储的 (例如 20 代表 20%)
            overlap_ratio = (document_settings.chunking_overlap or 20) / 100.0
            chunk_config = {
                "mode": document_settings.chunking_type,
                "max_size": document_settings.maximum_length,
                "overlap_ratio": overlap_ratio,
                "separators": document_settings.chunk_identifier.split(",") if document_settings.chunk_identifier else None
            }
            logger.debug(f"Chunk configuration for document {document_id}: {chunk_config}.")

            # 4. 创建并运行RAG管道
            # Embedding provider/model 可以将来从配置中读取
            pipeline = RAGPipeline(splitter_config=chunk_config)
            
            document_info = {
                "id": document.id,
                "name": document.file_name,
                "category_id": document.category_id,
                "user_id": document.create_by
            }

            # 定义一个简单的进度回调函数用于日志记录
            async def progress_logger(status: str, progress: float):
                logger.info(f"Doc {document_id} processing status: {status} ({progress*100:.0f}%)")
                # 在这里可以添加将进度发送到前端的逻辑 (例如, WebSocket)

            result = await pipeline.process_and_store_file(
                file_path=document.file_url,
                document_info=document_info,
                progress_callback=progress_logger
            )

            # 5. 更新文档状态
            document.status = 1  # 处理完成
            await db.commit()

            logger.info(f"Document processing completed successfully for document {document_id}.")
            return result

        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}", exc_info=True)
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
        logger.debug(f"Fetching document chunks for document {document_id}. Query: {query}, Top K: {top_k}.")
        try:
            # 1. 获取文档信息
            stmt = select(DocumentInfo).filter(
                DocumentInfo.id == document_id,
                DocumentInfo.is_deleted == 0
            )
            result = await db.execute(stmt)
            document = result.scalar_one_or_none()
            
            if not document:
                logger.error(f"Document {document_id} not found or already deleted when fetching chunks.")
                raise ValueError(f"文档不存在: {document_id}")

            # 2. 确定知识库类型和所有者ID
            kb_type = "department" if document.category_id else "personal"
            owner_id = document.category_id if kb_type == "department" else document.create_by
            logger.debug(f"KB Type: {kb_type}, Owner ID: {owner_id} for document {document_id}.")

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
                logger.debug(f"Performed similarity search for document {document_id}, returned {len(chunks)} chunks.")
            else:
                # 如果没有查询，直接返回文档的所有分块
                # 这里需要添加一个新的方法到 MilvusClient 中
                chunks = await processor.milvus_client.get_document_chunks(
                    collection_name=f"{kb_type}_kb",
                    document_id=document_id
                )
                logger.debug(f"Returned all chunks for document {document_id}: {len(chunks)} items.")

            return chunks

        except Exception as e:
            logger.error(f"Failed to get document chunks for document {document_id}: {e}", exc_info=True)
            raise

    @staticmethod
    async def search_similar_chunks(
        db: AsyncSession,
        document_id: int,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """搜索文档中相似的内容"""
        logger.info(f"Searching similar chunks for document {document_id} with query: {query[:50]}..., Top K: {top_k}.")
        return await DocumentService.get_document_chunks(
            db=db,
            document_id=document_id,
            query=query,
            top_k=top_k
        )