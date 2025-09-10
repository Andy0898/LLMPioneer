# app/core/celery_app.py
from celery import Celery
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)

# 创建 Celery 实例
celery_app = Celery(
    "knowledge_base",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    include=['app.core.celery.document_task']  # 显式包含任务模块
)

# Celery 配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 任务超时时间1小时
    worker_max_tasks_per_child=200,  # 每个worker最多执行200个任务后重启
    broker_connection_retry_on_startup=True,
    # 添加以下配置
    worker_prefetch_multiplier=1,  # 限制worker同时处理的任务数
    task_ignore_result=False,  # 需要获取任务结果
    task_always_eager=False,  # 确保任务异步执行
)

# 修改任务发现方式
# celery_app.autodiscover_tasks(['app'])  # 扫描整个app目录

# if __name__ == '__main__':
#     celery_app.start()