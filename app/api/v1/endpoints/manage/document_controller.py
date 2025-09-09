from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
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
from app.api.v1.deps import check_data_access_permission, require_permissions # 导入权限依赖
from app.services.permission_manager import PermissionManager # 导入权限管理器
from app.config.logger import get_logger # 导入日志

logger = get_logger(__name__) # 获取Logger实例

# router = APIRouter(dependencies=[Depends(deps.get_redis)])
router = APIRouter()

@router.post("/document/upload", response_model=List[DocumentInDB], dependencies=[Depends(require_permissions(["document:upload"]))]) # 添加权限
async def upload_enterprise_documents(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int = Form(...),
    files: List[UploadFile] = File(...),
    # description: str = Form(None),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[DocumentInDB]:
    """上传企业知识库文档"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to upload {len(files)} files to category {category_id}.")
    if len(files) > 10:
        logger.warning(f"User {current_user.id} attempted to upload {len(files)} files, exceeding limit of 10.")
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
        
    documents = []
    for file in files:
        if file.size > 100 * 1024 * 1024:  # 20MB
            logger.warning(f"File {file.filename} from user {current_user.id} exceeds 100MB limit.")
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 20MB limit")
            
        document = await DocumentService.create_document(
            db=db,
            file=file,
            category_id=category_id,
            user_id=current_user.id
            # description=description
        )
        documents.append(document)
    
    logger.info(f"Successfully uploaded {len(documents)} documents for user {current_user.id}.")
    return documents

# @router.get("/document/list", response_model=List[DocumentInDB])
@router.get("/document/list", response_model=List[DocumentInDB], dependencies=[Depends(require_permissions(["document:list"]))]) # 添加权限
async def get_enterprise_documents(
    db: AsyncSession = Depends(deps.get_db),
    category_id: int = None,
    skip: int = 0,
    limit: int = 10,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> List[DocumentInDB]:
    """获取企业知识库文档列表"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting document list. Category: {category_id}, Skip: {skip}, Limit: {limit}.")
    documents = await DocumentService.get_document_list(
        db=db,
        category_id=category_id,
        skip=skip,
        limit=limit
    )
    logger.info(f"Returned {len(documents)} documents to user {current_user.id}.")
    return documents

# @router.get("/document/{document_id}", response_model=DocumentInDB)
@router.get("/document/{document_id}", response_model=DocumentInDB, dependencies=[Depends(require_permissions(["document:read"]))]) # 添加权限
async def get_enterprise_document_detail(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user) # 仍需获取当前用户
) -> DocumentInDB:
    """根据ID获取企业知识库文档详情"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting detail for document {document_id}.")
    document = await DocumentService.get_by_id(db=db, document_id=document_id)
    if not document:
        logger.warning(f"Document {document_id} not found for detail request by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 使用 PermissionManager 进行数据访问权限检查
    permission_manager = PermissionManager(db)
    is_allowed = await permission_manager.validate_data_access(
        user_id=current_user.id,
        resource_owner_id=int(document.create_by), # 假设 create_by 是文档所有者的ID
        resource_org_id=document.category_id, # 假设 category_id 可以作为组织ID
        user_org_id=getattr(current_user, 'org_id', None) # 假设用户有 org_id 属性
    )

    if not is_allowed:
        logger.warning(f"User {current_user.id} not authorized to access document {document_id}.")
        raise HTTPException(status_code=403, detail="Not authorized to access this document")

    logger.info(f"Returned detail for document {document_id} to user {current_user.id}.")
    return document

# @router.delete("/document/{document_id}")
@router.delete("/document/{document_id}", dependencies=[Depends(require_permissions(["document:delete"]))]) # 添加权限
async def delete_enterprise_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> dict:
    """删除企业知识库文档"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to delete document {document_id}.")
    # 数据访问权限检查
    document = await DocumentService.get_by_id(db=db, document_id=document_id)
    if not document:
        logger.warning(f"Document {document_id} not found for deletion check by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Document not found")

    permission_manager = PermissionManager(db)
    is_allowed = await permission_manager.validate_data_access(
        user_id=current_user.id,
        resource_owner_id=int(document.create_by),
        resource_org_id=document.category_id,
        user_org_id=getattr(current_user, 'org_id', None)
    )
    if not is_allowed:
        logger.warning(f"User {current_user.id} not authorized to delete document {document_id}.")
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")

    success = await DocumentService.delete_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id
    )
    if not success:
        logger.error(f"Failed to delete document {document_id} for user {current_user.id} after authorization.")
        raise HTTPException(status_code=404, detail="Document not found")
    logger.info(f"Document {document_id} successfully deleted by user {current_user.id}.")
    return {"status": "success"}

# @router.post("/document/settings/create", response_model=DocumentSettingsInDB)
@router.post("/document/settings/create", response_model=DocumentSettingsInDB, dependencies=[Depends(require_permissions(["document:settings"]))]) # 添加权限
async def create_document_settings(
    document_settings_in: DocumentSettingsCreate,
    document_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)    
) -> DocumentSettingsInDB:
    """获取默认的文档解析设置"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to create settings for document {document_id} with data: {document_settings_in.dict()}")
    # 检查 document_id 是否已经有 Settings记录
    existing_settings = await DocumentService.get_document_settings(db=db, document_id=document_id)
    if existing_settings:
        logger.warning(f"Attempted to create settings for document {document_id} by user {current_user.id}, but settings already exist.")
        raise HTTPException(status_code=400, detail="Document settings already exist")
    document_settings_in.create_by = current_user.user_name
    # 调用 service 的方法新增一条记录
    new_settings = await DocumentService.create_document_settings(db=db, document_id=document_id, settings_in=document_settings_in, user_id=current_user.id)
    logger.info(f"Settings for document {document_id} created by user {current_user.id}.")
    return new_settings

@router.get("/document/settings/{document_id}", response_model=DocumentSettingsInDB)
async def get_document_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,    
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentSettingsInDB:
    """获取企业知识库文档设置"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting settings for document {document_id}.")
    settings = await DocumentService.get_document_settings(db=db, document_id=document_id)
    if not settings:
        logger.warning(f"Settings for document {document_id} not found for user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Document settings not found")
    logger.info(f"Returned settings for document {document_id} to user {current_user.id}.")
    return settings

# @router.put("/document/settings/{document_id}", response_model=DocumentSettingsInDB)
@router.put("/document/settings/{document_id}", response_model=DocumentSettingsInDB, dependencies=[Depends(require_permissions(["document:settings_update"]))]) # 添加权限
async def update_document_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    settings_in: DocumentSettingsCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentSettingsInDB:
    """更新企业知识库文档设置"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to update settings for document {document_id} with data: {settings_in.dict()}")
    # 数据访问权限检查 (与文档详情类似)
    document = await DocumentService.get_by_id(db=db, document_id=document_id)
    if not document:
        logger.warning(f"Associated document {document_id} not found for settings update by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Associated document not found")

    permission_manager = PermissionManager(db)
    is_allowed = await permission_manager.validate_data_access(
        user_id=current_user.id,
        resource_owner_id=int(document.create_by),
        resource_org_id=document.category_id,
        user_org_id=getattr(current_user, 'org_id', None)
    )
    if not is_allowed:
        logger.warning(f"User {current_user.id} not authorized to update settings for document {document_id}.")
        raise HTTPException(status_code=403, detail="Not authorized to update these settings")
    settings = await DocumentService.update_document_settings(
        db=db,
        document_id=document_id,
        settings_in=settings_in,
        user_id=current_user.id
    )
    logger.info(f"Settings for document {document_id} updated by user {current_user.id}.")
    return settings

# @router.post("/document/process/{document_id}", response_model=DocumentProcessResponse)
@router.post("/document/process/{document_id}", response_model=DocumentProcessResponse, dependencies=[Depends(require_permissions(["document:process"]))]) # 添加权限
async def process_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> DocumentProcessResponse:
    """处理企业知识库文档"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to process document {document_id}.")
    # 数据访问权限检查 (与文档详情类似)
    document = await DocumentService.get_by_id(db=db, document_id=document_id)
    if not document:
        logger.warning(f"Associated document {document_id} not found for processing by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Associated document not found")

    permission_manager = PermissionManager(db)
    is_allowed = await permission_manager.validate_data_access(
        user_id=current_user.id,
        resource_owner_id=int(document.create_by),
        resource_org_id=document.category_id,
        user_org_id=getattr(current_user, 'org_id', None)
    )
    if not is_allowed:
        logger.warning(f"User {current_user.id} not authorized to process document {document_id}.")
        raise HTTPException(status_code=403, detail="Not authorized to process this document")
    
    task = celery_app.send_task(
        "app.core.tasks.document_task.process_document",
        args=[document_id, current_user.id],
        queue='celery'  # 显式指定队列
    )
    logger.info(f"Document processing task {task.id} initiated for document {document_id} by user {current_user.id}.")
    return DocumentProcessResponse(task_id=task.id)

# @router.get("/document/progress/{task_id}", response_model=ProcessProgress)
@router.get("/document/progress/{task_id}", response_model=ProcessProgress, dependencies=[Depends(require_permissions(["document:process"]))]) # 添加权限
async def get_process_progress(
    *,
    task_id: str,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> ProcessProgress:
    """获取企业知识库文档处理进度"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting progress for task {task_id}.")
    task = celery_app.AsyncResult(task_id)
    if task.failed():
        logger.error(f"Task {task_id} failed. Error: {task.info}")
    logger.info(f"Returned progress for task {task_id} (status: {task.status}) to user {current_user.id}.")
    return ProcessProgress(
        status=task.status,
        progress=task.info.get('progress', 0) if task.info else 0,
        error=str(task.info) if task.failed() else None
    ) 