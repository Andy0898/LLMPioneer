from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.base import Base, TimestampMixin, OperatorMixin

class MessageModel(Base, TimestampMixin, OperatorMixin):
    """
    对话消息模型
    """
    __tablename__ = "ai_message"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='消息唯一ID')
    conversation_id = Column(BigInteger, ForeignKey('ai_conversation.id'), nullable=False, index=True, comment='所属对话ID')
    llm_id = Column(BigInteger, ForeignKey('ai_llm_configuration.id'), nullable=False, comment='大模型ID')
    question = Column(Text, nullable=False, comment='用户提问')
    content = Column(Text, nullable=False, comment='消息内容')
    reasoning_content = Column(Text, comment='推理文本')
    
    # 关联关系
    llm_config = relationship("LlmConfigurationModel", backref="messages")
    # create_by = Column(String(100))
    # create_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    # update_by = Column(String(100))
    # update_time = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow) 