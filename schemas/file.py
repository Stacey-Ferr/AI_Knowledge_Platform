from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class WarningsInfo(BaseModel):
    issue: str
    type: str

class FileMetadata(BaseModel):
    file_name: str
    file_type: str
    size_bytes: int
    uploaded_at: datetime
    element_count: int
    warnings: List[WarningsInfo] = Field(default_factory=list)

class IngestionResult(BaseModel):
    metadata: FileMetadata
    extracted_text: str
