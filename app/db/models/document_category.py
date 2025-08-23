from sqlalchemy import Column, Integer, String, DateTime, BigInteger, SmallInteger
from sqlalchemy.orm import relationship
from app.db.models.base import Base, TimestampMixin, OperatorMixin
from datetime import datetime

class DocumentCategory(Base, TimestampMixin, OperatorMixin):
    __tablename__ = "ai_document_category"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    code = Column(String(20), nullable=True, comment="类别编码：1001")
    name = Column(String(128), nullable=True, comment="类别名称: 如操作手册")
    description = Column(String(255), nullable=True, comment="类别描述：如系统操作使用手册文档")
    parent_id = Column(BigInteger, nullable=True, default=0, comment="父类别ID：0")
    user_id = Column(BigInteger, nullable=False, comment="用户ID。type=0的时候，填写默认值")
    type = Column(SmallInteger, nullable=False, default=0, comment="目录类型。0-企业知识库;1-个人知识库")
    status = Column(SmallInteger, nullable=True, default=1,comment="状态")
    is_deleted = Column(SmallInteger, nullable=True, default=0, comment="逻辑删除标志：0")
    sort_no = Column(Integer, nullable=True, comment="排序号：101")

    # 修改关系定义，使用 viewonly=True
    documents = relationship(
        "DocumentInfo",
        back_populates="category",
        # primaryjoin="and_(DocumentCategory.id==DocumentInfo.category_id, DocumentCategory.is_deleted==0)",
        primaryjoin="DocumentCategory.id==DocumentInfo.category_id",
        foreign_keys="DocumentInfo.category_id"
        # viewonly=True  # 添加这个参数表明这是一个只读关系
    )