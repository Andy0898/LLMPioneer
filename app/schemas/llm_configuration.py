from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class LlmConfigurationBase(BaseModel):
    llm_zh_name: str
    llm_en_name: str
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    top_p: float = 0
    temperature: float = 0
    max_tokens: int = 1024
    do_sample: bool = False
    max_chat_limit: int = 20
    status: int = 1
    is_local_llm: bool = False

class LlmConfigurationCreate(LlmConfigurationBase):
    create_by: Optional[str] = None

class LlmConfigurationUpdate(BaseModel):
    llm_zh_name: Optional[str] = None
    llm_en_name: Optional[str] = None
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    do_sample: Optional[bool] = None
    max_chat_limit: Optional[int] = None
    status: Optional[int] = None
    is_local_llm: Optional[bool] = None
    update_by: Optional[str] = None

class LlmConfigurationInDB(LlmConfigurationBase):
    id: int
    create_by: Optional[str] = None
    create_time: datetime
    update_by: Optional[str] = None
    update_time: datetime

    class Config:
        from_attributes = True

class LlmConfigurationResponse(LlmConfigurationInDB):
    pass 