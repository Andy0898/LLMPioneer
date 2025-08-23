from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# 会话基础模型
class ConversationBase(BaseModel):
    title: str = "新对话"
    user_id: int

# 创建会话请求模型
class ConversationCreate(ConversationBase):
    create_by: Optional[str] = None

# 更新会话请求模型
class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    update_by: Optional[str] = None

# 会话响应模型
class ConversationInDB(ConversationBase):
    id: int
    create_by: Optional[str] = None
    create_time: datetime
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConversationResponse(ConversationInDB):
    initial_response: Optional[Dict[str, Any]] = None

# 会话列表响应模型
class ConversationList(BaseModel):
    total: int
    items: List[ConversationResponse] 