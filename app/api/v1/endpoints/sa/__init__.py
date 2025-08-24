from fastapi import APIRouter
from .conversation_controller import router as conversation_router
from .llm_configuration_controller import router as llm_configuration_router
from .message_controller import router as message_router
from .document_category_controller import router as knowledge_category_router
from .document_controller import router as knowledge_document_router


router = APIRouter()
 
router.include_router(conversation_router, prefix="/conversation", tags=["对话管理"]) 
router.include_router(llm_configuration_router, prefix="/llm", tags=["LLM配置管理"])
router.include_router(message_router, prefix="/message", tags=["消息管理"])
router.include_router(knowledge_category_router, prefix="/knowledge", tags=["企业知识库分类管理"])
router.include_router(knowledge_document_router, prefix="/knowledge", tags=["企业知识库文档管理"])