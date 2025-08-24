from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, SmallInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.models.base import Base, TimestampMixin, OperatorMixin
from datetime import datetime

if TYPE_CHECKING:
    from .document_info import DocumentInfo

class DocumentSettings(Base, TimestampMixin, OperatorMixin):
    __tablename__ = "ai_document_settings"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    document_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="文档ID")
    parse_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, comment="解析方式，0-快速解析；1:精准解析")
    chunking_type: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, comment="0-自动分段和预处理；1-按层级分段；2-自定义分段")
    chunk_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="分段标识符,chunking_type=2时")
    maximum_length: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="分段最大长度,chunking_type=2时")
    chunking_overlap: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="分段重叠度,chunking_type=2时")

    document: Mapped[Optional["DocumentInfo"]] = relationship(
        back_populates="settings", 
        primaryjoin="DocumentSettings.document_id==DocumentInfo.id",
        foreign_keys="[DocumentSettings.document_id]"
    )

    __table_args__ = {'extend_existing': True}
