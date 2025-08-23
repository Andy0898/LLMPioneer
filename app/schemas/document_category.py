from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class DocumentCategoryBase(BaseModel):
    code: Optional[str] = None
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = 0
    type: Optional[int] = 0
    sort_no: Optional[int] = 100

class DocumentCategoryCreate(DocumentCategoryBase):
    create_by: Optional[str] = None 

class DocumentCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sort_no: Optional[int] = None
    update_by: Optional[str] = None

class DocumentCategoryInDB(DocumentCategoryBase):
    id: int
    user_id: int
    status: Optional[int] = 1
    is_deleted: Optional[int] = 0
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentCategoryTree(DocumentCategoryInDB):
    children: Optional[List['DocumentCategoryTree']] = None

# DocumentCategoryTree.update_forward_refs()
DocumentCategoryTree.model_rebuild()