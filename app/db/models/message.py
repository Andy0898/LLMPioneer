from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.models.base import Base, TimestampMixin, OperatorMixin

if TYPE_CHECKING:
    from .llm_configuration import LlmConfigurationModel
    from .conversation import ConversationModel

class MessageModel(Base, TimestampMixin, OperatorMixin):
    """
    对话消息模型
    """
    __tablename__ = "ai_message"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment='消息唯一ID')
    conversation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('ai_conversation.id'), nullable=False, index=True, comment='所属对话ID')
    llm_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('ai_llm_configuration.id'), nullable=False, comment='大模型ID')
    question: Mapped[str] = mapped_column(Text, nullable=False, comment='用户提问')
    content: Mapped[str] = mapped_column(Text, nullable=False, comment='消息内容')
    reasoning_content: Mapped[str | None] = mapped_column(Text, comment='推理文本')
    
    # 关联关系
    llm_config: Mapped["LlmConfigurationModel"] = relationship(backref="messages")
    conversation: Mapped["ConversationModel"] = relationship(back_populates="messages")

    __table_args__ = {'extend_existing': True}
