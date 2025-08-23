from sqlalchemy import Column, Integer, String, BigInteger, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.base import Base, TimestampMixin, OperatorMixin
from datetime import datetime

class DocumentInfo(Base, TimestampMixin, OperatorMixin):
    __tablename__ = "ai_document_info"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    file_name = Column(String(255), nullable=True, comment="文件名称")
    category_id = Column(BigInteger, nullable=True, comment="所属类目")
    # category_id = Column(BigInteger, ForeignKey('ai_document_category.id'), nullable=True, comment="所属类目")  # 添加外键约束
    version_no = Column(String(255), nullable=True, comment="内容版本号")
    file_url = Column(String(1024), nullable=True, comment="原文地址")
    status = Column(SmallInteger, nullable=True, default=1, comment="状态")
    sort_no = Column(Integer, nullable=True, comment="排序号")
    is_deleted = Column(SmallInteger, nullable=True, default=0, comment="逻辑删除标志")
    
    # 关联关系，不使用外键约束
    # 修改关系定义，使用 viewonly=True
    category = relationship(
        "DocumentCategory",
        back_populates="documents",
        primaryjoin="DocumentCategory.id==DocumentInfo.category_id",
        foreign_keys="DocumentInfo.category_id"
        # viewonly=True  # 添加这个参数表明这是一个只读关系
    )
    settings = relationship(
        "DocumentSettings", 
        back_populates="document", 
        uselist=False, 
        primaryjoin="DocumentInfo.id==DocumentSettings.document_id",
        foreign_keys="DocumentSettings.document_id"
        # viewonly=True  # 添加这个参数表明这是一个只读关系
    )