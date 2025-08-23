from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class MessageBase(BaseModel):
    conversation_id: int
    llm_id: int
    question: str
    content: Optional[str] = None
    reasoning_content: Optional[str] = None

class MessageCreate(MessageBase):
    create_by: Optional[str] = None

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    reasoning_content: Optional[str] = None
    update_by: Optional[str] = None

class MessageInDB(MessageBase):
    id: int
    create_by: Optional[str] = None
    create_time: datetime
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class MessageResponse(MessageInDB):
    pass 