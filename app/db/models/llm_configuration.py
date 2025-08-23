from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Float, Boolean
from app.db.models.base import Base, TimestampMixin, OperatorMixin

class LlmConfigurationModel(Base, TimestampMixin, OperatorMixin):
    """
    LLM配置模型
    """
    __tablename__ = "ai_llm_configuration"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键')
    llm_zh_name = Column(String(100), nullable=False, comment='大模型中文名称')
    llm_en_name = Column(String(100), nullable=False, unique=True, comment='大模型英文简称')
    api_key = Column(String(255), comment='大模型的API Key')
    api_url = Column(String(255), comment='大模型的API URL')
    top_p = Column(Float, default=0, comment='生成过程中的核采样方法概率阈值')
    temperature = Column(Float, default=0, comment='用于控制模型回复的随机性和多样性')
    max_tokens = Column(BigInteger, default=1024, comment='模型可生成的最大token个数')
    do_sample = Column(Boolean, default=False, comment='启用采样策略')
    max_chat_limit = Column(BigInteger, default=20, comment='多轮对话次数')
    status = Column(Integer, default=1, comment='LLM状态，1：激活；0：不可用')
    is_local_llm = Column(Boolean, nullable=False, default=False, comment='是否本地大模型')
