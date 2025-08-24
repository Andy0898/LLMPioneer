from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.models.base import Base, TimestampMixin, OperatorMixin

if TYPE_CHECKING:
    from .user import UserModel
    from .message import MessageModel

class ConversationModel(Base, TimestampMixin, OperatorMixin):
    """
    对话会话模型
    """
    __tablename__ = 'ai_conversation'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment='会话唯一ID')
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('t_sys_user.id'), nullable=False, comment='所属用户')
    title: Mapped[str] = mapped_column(String(255), nullable=False, default='新对话', comment='对话标题')
    
    # 关联关系
    user: Mapped["UserModel"] = relationship(back_populates="conversations")
    messages: Mapped[List["MessageModel"]] = relationship(
        back_populates="conversation", 
        lazy="dynamic", 
        cascade="all, delete-orphan"
    )

    __table_args__ = {'extend_existing': True}
