import logging
from logging.handlers import RotatingFileHandler
import os
from app.config.settings import settings

def get_logger(name: str) -> logging.Logger:
    """
    获取一个配置好的Logger实例。
    如果Logger已经配置过，则直接返回。
    """
    logger = logging.getLogger(name)

    # 避免重复添加Handler
    if not logger.handlers:
        # 设置日志级别
        logger.setLevel(settings.LOG_LEVEL.upper())

        # 创建日志格式器
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(thread)d - %(filename)s:%(lineno)d - %(message)s'
        )

        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # 文件输出 (带轮转)
        log_file_path = os.path.join(settings.LOG_PATH, "app.log")
        # 确保日志目录存在
        os.makedirs(settings.LOG_PATH, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,              # 最多保留5个备份文件
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

# 初始化根Logger，确保在应用启动时配置好
# 这样即使没有显式调用get_logger，basicConfig的默认行为也会被我们的配置覆盖
# 并且可以确保所有通过logging.getLogger()获取的logger都继承这些handler
root_logger = logging.getLogger()
if not root_logger.handlers:
    root_logger.setLevel(settings.LOG_LEVEL.upper())
    
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(thread)d - %(filename)s:%(lineno)d - %(message)s'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    log_file_path = os.path.join(settings.LOG_PATH, "app.log")
    os.makedirs(settings.LOG_PATH, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

# 移除可能由basicConfig()添加的默认handler，避免重复输出
for handler in logging.root.handlers[:]:
    if isinstance(handler, logging.StreamHandler) and handler.stream == None: # 检查是否是basicConfig添加的默认handler
        logging.root.removeHandler(handler)
