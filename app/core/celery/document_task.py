from typing import Dict, Any
import asyncio
from celery import Task
from .celery_app import celery_app
from app.api.v1.deps import get_db
from app.db.session import AsyncSessionLocal
from app.services.document_service import DocumentService
from app.config.logger import get_logger

log = get_logger(__name__)

class DocumentProcessTask(Task):
    """文档处理任务基类"""
    _db = None
    
    def after_return(self, *args, **kwargs):
        """任务完成后关闭数据库连接"""
        if self._db is not None:
            self._db.close()
            self._db = None

@celery_app.task(
    name='app.core.tasks.document_task.process_document',
    base=DocumentProcessTask,
    bind=True
)

def process_document(self, document_id: int, user_id: int) -> Dict[str, Any]:
    """处理文档任务"""
    try:
        # 创建事件循环来运行异步代码
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def process():
            try:
                # 使用异步上下文管理器创建会话
                async with AsyncSessionLocal() as db:
                # db = await anext(get_db())
                    # 获取文档信息
                    document = await DocumentService.get_by_id(db, document_id)
                    if not document:
                        raise ValueError(f"Document {document_id} not found")
                        
                    # 获取文档设置
                    settings = await DocumentService.get_document_settings(db, document_id)
                    if not settings:
                        raise ValueError(f"Document settings for {document_id} not found")
                    
                    # 更新任务进度 - 开始
                    self.update_state(
                        state='PROGRESS',
                        meta={'progress': 10, 'status': 'Processing document...'}
                    )
                    
                    # 处理文档
                    chunks = await DocumentService.process_document(
                        db=db,
                        document_id=document_id
                    )
                    
                    # 更新任务进度 - 完成
                    self.update_state(
                        state='PROGRESS',
                        meta={'progress': 100, 'status': 'Document processed successfully'}
                    )
                    
                    return {
                        'status': 'success',
                        'progress': 100,
                        'document_id': document_id,
                        'chunks_count': len(chunks) if chunks else 0
                    }
            except Exception as e:
                log.error(f"处理文档时出错: {str(e)}")
                raise
                
        # 运行异步任务
        result = loop.run_until_complete(process())
        loop.close()
        return result
        
    except Exception as e:
        log.error(f"处理文档任务失败: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'document_id': document_id
        }