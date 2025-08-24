from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
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

router = APIRouter(dependencies=[Depends(deps.get_redis)])

@router.post("/document/upload", response_model=List[DocumentInDB])
async def upload_enterprise_documents(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int = Form(...),
    files: List[UploadFile] = File(...),
    # description: str = Form(None),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[DocumentInDB]:
    """上传企业知识库文档"""
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

@router.get("/document/list", response_model=List[DocumentInDB])
async def get_enterprise_documents(
    db: AsyncSession = Depends(deps.get_db),
    category_id: int = None,
    skip: int = 0,
    limit: int = 10,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[DocumentInDB]:
    """获取企业知识库文档列表"""
    documents = await DocumentService.get_document_list(
        db=db,
        category_id=category_id,
        skip=skip,
        limit=limit
    )
    return documents

# ... 其他路由处理器的 Session 类型也需要改为 AsyncSession

@router.delete("/document/{document_id}")
async def delete_enterprise_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> dict:
    """删除企业知识库文档"""
    success = await DocumentService.delete_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success"}

@router.post("/document/settings/create", response_model=DocumentSettingsInDB)
async def create_document_settings(
    document_settings_in: DocumentSettingsCreate,
    document_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)    
) -> DocumentSettingsInDB:
    """获取默认的文档解析设置"""
    # 检查是否有管理员权限
    # if not current_user.get("is_admin"):
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # 检查 document_id 是否已经有 Settings记录
    existing_settings = await DocumentService.get_document_settings(db=db, document_id=document_id)
    if existing_settings:
        raise HTTPException(status_code=400, detail="Document settings already exist")
    document_settings_in.create_by = current_user.user_name
    # 调用 service 的方法新增一条记录
    new_settings = await DocumentService.create_document_settings(db=db, document_id=document_id, settings_in=document_settings_in, user_id=current_user.id)
    return new_settings

@router.get("/document/settings/{document_id}", response_model=DocumentSettingsInDB)
async def get_document_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,    
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentSettingsInDB:
    """获取企业知识库文档设置"""
    settings = await DocumentService.get_document_settings(db=db, document_id=document_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Document settings not found")
    return settings

@router.put("/document/settings/{document_id}", response_model=DocumentSettingsInDB)
async def update_document_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    settings_in: DocumentSettingsCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentSettingsInDB:
    """更新企业知识库文档设置"""
    settings_in.create_by = current_user.user_name
    settings = await DocumentService.update_document_settings(
        db=db,
        document_id=document_id,
        settings_in=settings_in,
        user_id=current_user.id
    )
    return settings

@router.post("/document/process/{document_id}", response_model=DocumentProcessResponse)
async def process_document(
    *,
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentProcessResponse:
    """处理企业知识库文档"""
    task = celery_app.send_task(
        "app.core.tasks.document_task.process_document",
        args=[document_id, current_user.id],
        queue='celery'  # 显式指定队列
    )
    return DocumentProcessResponse(task_id=task.id)

@router.get("/document/progress/{task_id}", response_model=ProcessProgress)
async def get_process_progress(
    *,
    task_id: str,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> ProcessProgress:
    """获取企业知识库文档处理进度"""
    task = celery_app.AsyncResult(task_id)
    return ProcessProgress(
        status=task.status,
        progress=task.info.get('progress', 0) if task.info else 0,
        error=str(task.info) if task.failed() else None
    ) 