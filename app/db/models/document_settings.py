from sqlalchemy import Column, Integer, String, DateTime, BigInteger, SmallInteger
from sqlalchemy.orm import relationship
from app.db.models.base import Base, TimestampMixin, OperatorMixin
from datetime import datetime

class DocumentSettings(Base, TimestampMixin, OperatorMixin):
    __tablename__ = "ai_document_settings"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    document_id = Column(BigInteger, nullable=False, comment="文档ID")
    parse_level = Column(SmallInteger, nullable=False, default=0, comment="解析方式，0-快速解析；1:精准解析")
    chunking_type = Column(SmallInteger, nullable=False, default=0, comment="0-自动分段和预处理；1-按层级分段；2-自定义分段")
    chunk_identifier = Column(String(255), nullable=True, comment="分段标识符,chunking_type=2时")
    maximum_length = Column(Integer, nullable=True, comment="分段最大长度,chunking_type=2时")
    chunking_overlap = Column(Integer, nullable=True, comment="分段重叠度,chunking_type=2时")
    # create_by = Column(String(100), nullable=True, comment="创建人")
    # create_time = Column(DateTime, nullable=True, default=datetime.now, comment="创建时间")
    # update_by = Column(String(100), nullable=True, comment="更新人")
    # update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新时间") 

    # 关联关系，不使用外键约束
    document = relationship(
        "DocumentInfo", 
        back_populates="settings", 
        primaryjoin="DocumentSettings.document_id==DocumentInfo.id",
        foreign_keys="DocumentSettings.document_id"
    )