from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession  # 修改这里
from app.api.v1 import deps
from app.db.models.user import UserModel
from app.core.celery_app import celery_app
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
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
        
    documents = []
    for file in files:
        if file.size > 20 * 1024 * 1024:  # 20MB
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 20MB limit")
            
        document = await DocumentService.create_document(
            db=db,
            file=file,
            category_id=category_id,
            user_id=current_user.id
            # description=description
        )
        documents.append(document)
    
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
    documents = await DocumentService.get_document_list(
        db=db,
        category_id=category_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return documents

@router.delete("/knowledge/document/{document_id}")
async def delete_personal_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> dict:
    """删除个人知识库文档"""
    success = await DocumentService.delete_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success"}

@router.get("/knowledge/document/settings/{document_id}", response_model=DocumentSettingsInDB)
async def get_personal_document_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentSettingsInDB:
    """获取个人知识库文档设置"""
    settings = await DocumentService.get_document_settings(db=db, document_id=document_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Document settings not found")
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
    settings = await DocumentService.update_document_settings(
        db=db,
        document_id=document_id,
        settings_in=settings_in,
        user_id=current_user.id
    )
    return settings

@router.post("/knowledge/document/process/{document_id}", response_model=DocumentProcessResponse)
async def process_personal_document(
    *,
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentProcessResponse:
    """处理个人知识库文档"""
    task = celery_app.send_task(
        "app.core.tasks.document_task.process_document",
        args=[document_id, current_user.id],
        queue='celery'  # 显式指定队列
    )
    return DocumentProcessResponse(task_id=task.id)

@router.get("/knowledge/document/progress/{task_id}", response_model=ProcessProgress)
async def get_personal_process_progress(
    *,
    task_id: str,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> ProcessProgress:
    """获取个人知识库文档处理进度"""
    task = celery_app.AsyncResult(task_id)
    return ProcessProgress(
        status=task.status,
        progress=task.info.get('progress', 0) if task.info else 0,
        error=str(task.info) if task.failed() else None
    ) 