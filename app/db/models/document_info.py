from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, Integer, String, BigInteger, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.models.base import Base, TimestampMixin, OperatorMixin
from datetime import datetime

if TYPE_CHECKING:
    from .document_category import DocumentCategory
    from .document_settings import DocumentSettings

class DocumentInfo(Base, TimestampMixin, OperatorMixin):
    __tablename__ = "ai_document_info"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="文件名称")
    category_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="所属类目")
    version_no: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="内容版本号")
    file_url: Mapped[str | None] = mapped_column(String(1024), nullable=True, comment="原文地址")
    status: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, default=1, comment="状态")
    sort_no: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="排序号")
    is_deleted: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, default=0, comment="逻辑删除标志")
    
    category: Mapped[Optional["DocumentCategory"]] = relationship(
        back_populates="documents",
        primaryjoin="DocumentCategory.id==DocumentInfo.category_id",
        foreign_keys="[DocumentInfo.category_id]"
    )
    settings: Mapped[Optional["DocumentSettings"]] = relationship(
        back_populates="document", 
        uselist=False, 
        primaryjoin="DocumentInfo.id==DocumentSettings.document_id",
        foreign_keys="[DocumentSettings.document_id]"
    )

    __table_args__ = {'extend_existing': True}
