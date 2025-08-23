import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)