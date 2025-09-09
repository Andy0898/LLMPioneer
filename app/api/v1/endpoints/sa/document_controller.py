from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession  # 修改这里
from app.api.v1 import deps
from app.db.models.user import UserModel
from app.core.celery.celery_app import celery_app
from app.schemas.document import (
    DocumentCreate,
    DocumentInDB,
    DocumentProcessResponse,
    ProcessProgress
)
from app.schemas.document import (
    DocumentSettingsCreate,
    DocumentSettingsUpdate,
    DocumentSettingsInDB
)
from app.services.document_service import DocumentService
from app.config.logger import get_logger # 导入日志

logger = get_logger(__name__) # 获取Logger实例

router = APIRouter()

@router.post("/knowledge/document/upload", response_model=List[DocumentInDB])
async def upload_personal_documents(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int = Form(...),
    files: List[UploadFile] = File(...),
    # description: str = Form(None),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[DocumentInDB]:
    """上传个人知识库文档"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to upload {len(files)} personal documents to category {category_id}.")
    if len(files) > 10:
        logger.warning(f"User {current_user.id} attempted to upload {len(files)} files, exceeding limit of 10.")
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
        
    documents = []
    for file in files:
        if file.size > 20 * 1024 * 1024:  # 20MB
            logger.warning(f"File {file.filename} from user {current_user.id} exceeds 20MB limit.")
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 20MB limit")
            
        document = await DocumentService.create_document(
            db=db,
            file=file,
            category_id=category_id,
            user_id=current_user.id
            # description=description
        )
        documents.append(document)
    
    logger.info(f"Successfully uploaded {len(documents)} personal documents for user {current_user.id}.")
    return documents

@router.get("/knowledge/document/list", response_model=List[DocumentInDB])
async def get_personal_documents(
    db: AsyncSession = Depends(deps.get_db),
    category_id: int = None,
    skip: int = 0,
    limit: int = 10,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[DocumentInDB]:
    """获取个人知识库文档列表"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting personal document list. Category: {category_id}, Skip: {skip}, Limit: {limit}.")
    documents = await DocumentService.get_document_list(
        db=db,
        category_id=category_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    logger.info(f"Returned {len(documents)} personal documents to user {current_user.id}.")
    return documents

@router.delete("/knowledge/document/{document_id}")
async def delete_personal_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> dict:
    """删除个人知识库文档"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to delete personal document {document_id}.")
    success = await DocumentService.delete_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id
    )
    if not success:
        logger.warning(f"Personal document {document_id} not found for deletion by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Document not found")
    logger.info(f"Personal document {document_id} deleted by user {current_user.id}.")
    return {"status": "success"}

@router.get("/knowledge/document/settings/{document_id}", response_model=DocumentSettingsInDB)
async def get_personal_document_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentSettingsInDB:
    """获取个人知识库文档设置"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting settings for personal document {document_id}.")
    settings = await DocumentService.get_document_settings(db=db, document_id=document_id)
    if not settings:
        logger.warning(f"Settings for personal document {document_id} not found for user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Document settings not found")
    logger.info(f"Returned settings for personal document {document_id} to user {current_user.id}.")
    return settings

@router.put("/knowledge/document/settings/{document_id}", response_model=DocumentSettingsInDB)
async def update_personal_document_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    settings_in: DocumentSettingsCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentSettingsInDB:
    """更新个人知识库文档设置"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to update settings for personal document {document_id} with data: {settings_in.dict()}")
    settings = await DocumentService.update_document_settings(
        db=db,
        document_id=document_id,
        settings_in=settings_in,
        user_id=current_user.id
    )
    logger.info(f"Settings for personal document {document_id} updated by user {current_user.id}.")
    return settings

@router.post("/knowledge/document/process/{document_id}", response_model=DocumentProcessResponse)
async def process_personal_document(
    *,
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentProcessResponse:
    """处理个人知识库文档"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to process personal document {document_id}.")
    task = celery_app.send_task(
        "app.core.tasks.document_task.process_document",
        args=[document_id, current_user.id],
        queue='celery'  # 显式指定队列
    )
    logger.info(f"Personal document processing task {task.id} initiated for document {document_id} by user {current_user.id}.")
    return DocumentProcessResponse(task_id=task.id)

@router.get("/knowledge/document/progress/{task_id}", response_model=ProcessProgress)
async def get_personal_process_progress(
    *,
    task_id: str,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> ProcessProgress:
    """获取个人知识库文档处理进度"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting progress for personal document task {task_id}.")
    task = celery_app.AsyncResult(task_id)
    if task.failed():
        logger.error(f"Personal document task {task_id} failed. Error: {task.info}")
    logger.info(f"Returned progress for personal document task {task_id} (status: {task.status}) to user {current_user.id}.")
    return ProcessProgress(
        status=task.status,
        progress=task.info.get('progress', 0) if task.info else 0,
        error=str(task.info) if task.failed() else None
    ) 