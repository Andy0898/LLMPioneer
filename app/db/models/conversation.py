from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.models.base import Base, TimestampMixin, OperatorMixin

class ConversationModel(Base, TimestampMixin, OperatorMixin):
    """
    对话会话模型
    """
    __tablename__ = 'ai_conversation'  # 使用实际的表名
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='会话唯一ID')
    user_id = Column(BigInteger, ForeignKey('t_sys_user.id'), nullable=False, comment='所属用户')
    title = Column(String(255), nullable=False, default='新对话', comment='对话标题')
    
    # 关联关系
    user = relationship("UserModel", backref="conversations")
    messages = relationship("MessageModel", backref="conversation", lazy="dynamic") 