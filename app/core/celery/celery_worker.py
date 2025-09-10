# celery_worker.py
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))
import os

from app.core.celery.celery_app import celery_app

if __name__ == '__main__':
    # 确保 app 目录在 Python 路径中
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    celery_app.worker_main(argv=['worker', '--loglevel=info', '--pool=solo'])