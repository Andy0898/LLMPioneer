from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, SmallInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.models.base import Base, TimestampMixin, OperatorMixin
from datetime import datetime

if TYPE_CHECKING:
    from .document_info import DocumentInfo

class DocumentCategory(Base, TimestampMixin, OperatorMixin):
    __tablename__ = "ai_document_category"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    code: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="类别编码：1001")
    name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="类别名称: 如操作手册")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="类别描述：如系统操作使用手册文档")
    parent_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=0, comment="父类别ID：0")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID。type=0的时候，填写默认值")
    type: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, comment="目录类型。0-企业知识库;1-个人知识库")
    status: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, default=1,comment="状态")
    is_deleted: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, default=0, comment="逻辑删除标志：0")
    sort_no: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="排序号：101")

    documents: Mapped[List["DocumentInfo"]] = relationship(
        back_populates="category",
        primaryjoin="DocumentCategory.id==DocumentInfo.category_id",
        foreign_keys="[DocumentInfo.category_id]"
    )

    __table_args__ = {'extend_existing': True}