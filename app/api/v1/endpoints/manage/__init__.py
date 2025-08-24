from fastapi import APIRouter
from .user_controller import router as user_router
from .role_controller import router as role_router
from .permission_controller import router as permission_router
from .document_category_controller import router as knowledge_category_router
from .document_controller import router as knowledge_document_router

router = APIRouter()
 
router.include_router(user_router, prefix="/user", tags=["用户管理"])
router.include_router(role_router, prefix="/role", tags=["角色管理"])
router.include_router(permission_router, prefix="/permission", tags=["权限管理"]) 
router.include_router(knowledge_category_router, prefix="/knowledge", tags=["企业知识库分类管理"])
router.include_router(knowledge_document_router, prefix="/knowledge", tags=["企业知识库文档管理"])