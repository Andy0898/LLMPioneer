# app/config/settings.py
from typing import Any, Dict, Optional, List, Set
from pydantic import MySQLDsn, validator, Field
from pydantic_settings import BaseSettings
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    """应用配置类"""
    
    # ==================== 项目基础配置 ====================
    PROJECT_NAME: str = Field(default="LLM Pioneer", description="项目名称")
    VERSION: str = Field(default="1.0.0", description="项目版本")
    API_V1_STR: str = Field(default="/api/v1", description="API版本路径")
    DEBUG: bool = Field(default=True, description="调试模式")
    
    # ==================== 服务器配置 ====================
    HOST: str = Field(default="127.0.0.1", description="服务器主机")
    PORT: int = Field(default=18000, description="服务器端口")
    
    # ==================== 安全配置 ====================
    SECRET_KEY: str = Field(
        default="your-secret-key-here", 
        description="JWT密钥"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24,  # 24小时
        description="访问令牌过期时间（分钟）"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT算法")
    
    # ==================== 数据库配置 ====================
    MYSQL_HOST: str = Field(default="localhost", description="MySQL主机")
    MYSQL_PORT: str = Field(default="3306", description="MySQL端口")
    MYSQL_USER: str = Field(default="root", description="MySQL用户名")
    MYSQL_PASSWORD: str = Field(default="Abcd1234", description="MySQL密码")
    MYSQL_DATABASE: str = Field(default="sadb", description="MySQL数据库名")
    SQLALCHEMY_DATABASE_URI: Optional[MySQLDsn] = None
    
    # ==================== Redis配置 ====================
    REDIS_HOST: str = Field(default="localhost", description="Redis主机")
    REDIS_PORT: int = Field(default=6379, description="Redis端口")
    REDIS_DB: int = Field(default=0, description="Redis数据库")
    
    # ==================== Milvus配置 ====================
    MILVUS_HOST: str = Field(default="169.169.128.101", description="Milvus主机")
    MILVUS_PORT: int = Field(default=19531, description="Milvus端口")
    MILVUS_USER: str = Field(default="root", description="Milvus用户名")
    MILVUS_PASSWORD: str = Field(default="123456", description="Milvus密码")
    
    # ==================== 文档上传配置 ====================
    UPLOAD_DIR: str = Field(default="uploads", description="上传目录")
    MAX_UPLOAD_SIZE: int = Field(
        default=20 * 1024 * 1024,  # 20MB
        description="最大上传文件大小（字节）"
    )
    ALLOWED_EXTENSIONS: Set[str] = Field(
        default={'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png'},
        description="允许的文件扩展名"
    )
    
    # ==================== 跨域配置 ====================
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["*"], 
        description="允许的跨域来源"
    )
    
    # ==================== 日志配置 ====================
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_PATH: str = Field(
        default_factory=lambda: str(Path(__file__).parent.parent / "logs"),
        description="日志路径"
    )
    
    # ==================== 验证器 ====================
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """构建数据库连接URI"""
        if isinstance(v, str):
            return v
        return MySQLDsn.build(
            scheme="mysql+aiomysql",
            username=values.get("MYSQL_USER"),
            password=values.get("MYSQL_PASSWORD"),
            host=values.get("MYSQL_HOST"),
            port=int(values.get("MYSQL_PORT")),
            path=values.get("MYSQL_DATABASE") or ""
        )
    
    @validator("UPLOAD_DIR")
    def create_upload_dir(cls, v: str) -> str:
        """确保上传目录存在"""
        os.makedirs(v, exist_ok=True)
        return v
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_allowed_extensions(cls, v: Any) -> Set[str]:
        """解析允许的文件扩展名"""
        if isinstance(v, str):
            # 如果是字符串，按逗号分割
            return set(ext.strip() for ext in v.split(",") if ext.strip())
        elif isinstance(v, (list, set)):
            # 如果是列表或集合，直接转换
            return set(v)
        return v
    
    @validator("MAX_UPLOAD_SIZE", pre=True)
    def parse_max_upload_size(cls, v: Any) -> int:
        """解析最大上传文件大小"""
        if isinstance(v, str):
            # 如果是字符串，尝试转换为整数
            try:
                return int(v)
            except ValueError:
                # 如果转换失败，尝试解析带单位的字符串（如 "20MB"）
                if v.upper().endswith("MB"):
                    size_mb = int(v[:-2])
                    return size_mb * 1024 * 1024
                elif v.upper().endswith("KB"):
                    size_kb = int(v[:-2])
                    return size_kb * 1024
                else:
                    raise ValueError(f"无法解析文件大小: {v}")
        return int(v)
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建配置实例
settings = Settings()

# 确保必要的目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.LOG_PATH, exist_ok=True)