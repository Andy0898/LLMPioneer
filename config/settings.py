from typing import Any, Dict, Optional, List
from pydantic import MySQLDsn, validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    # 项目基础配置
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "sa-plus")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # Redis配置（用于Celery）
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    REDIS_DB: int = os.getenv("REDIS_DB", 0)

    # Milvus配置
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "169.169.128.101")
    MILVUS_PORT: int = os.getenv("MILVUS_PORT", 19531)
    MILVUS_USER: str = os.getenv("MILVUS_USER", "root")
    MILVUS_PASSWORD: str = os.getenv("MILVUS_PASSWORD", "123456")

    # 文档上传配置
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE: int = os.getenv("MAX_UPLOAD_SIZE", 20 * 1024 * 1024)  # 20MB
    ALLOWED_EXTENSIONS: set = os.getenv("ALLOWED_EXTENSIONS", {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png'})

    
    # 数据库配置
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "Abcd1234")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "sadb")
    SQLALCHEMY_DATABASE_URI: Optional[MySQLDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return MySQLDsn.build(
            scheme="mysql+aiomysql",
            username=values.get("MYSQL_USER"),
            password=values.get("MYSQL_PASSWORD"),
            host=values.get("MYSQL_HOST"),
            port=int(values.get("MYSQL_PORT")),
            path=values.get("MYSQL_DATABASE") or ""  # 移除前导斜杠
        )
    
    # 跨域配置
    BACKEND_CORS_ORIGINS: list = ["*"]

    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # 文档上传配置
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str("20")))  # 默认20MB
    ALLOWED_EXTENSIONS: List[str] = os.getenv("ALLOWED_EXTENSIONS", ".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png").split(",")


    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_PATH: str = str(Path(__file__).parent.parent / "logs")
    
    @validator("UPLOAD_DIR")
    def create_upload_dir(cls, v):
        """确保上传目录存在"""
        os.makedirs(v, exist_ok=True)
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 
# 验证必要的目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)