from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from fastapi import UploadFile

class DocumentBase(BaseModel):
    category_id: int
    # description: Optional[str] = None

class DocumentCreate(DocumentBase):
    files: List[UploadFile]
    create_by: Optional[str] = None

class DocumentUpdate(BaseModel):
    update_by: Optional[str] = None
    status: Optional[int] = None

class DocumentInDB(DocumentBase):
    id: int
    file_name: str
    file_url: str
    version_no: Optional[str] = None
    status: Optional[int] = None
    sort_no: Optional[int] = None
    is_deleted: Optional[int] = 0
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentSettingsBase(BaseModel):
    parse_level: int = 0
    chunking_type: int = 0
    chunk_identifier: Optional[str] = None
    maximum_length: Optional[int] = None
    chunking_overlap: Optional[int] = None

class DocumentSettingsCreate(DocumentSettingsBase):
    create_by: Optional[str] = None    

class DocumentSettingsUpdate(DocumentSettingsBase):
    update_by: Optional[str] = None

class DocumentSettingsInDB(DocumentSettingsBase):
    id: int
    document_id: int
    create_by: Optional[str] = None
    create_time: Optional[datetime] = None
    update_by: Optional[str] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentProcessResponse(BaseModel):
    task_id: str

class ProcessProgress(BaseModel):
    status: str
    progress: float
    error: Optional[str] = None 