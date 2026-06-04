from pydantic import BaseModel
from typing import Optional

class HealthResponse(BaseModel):
    service: str
    status: str

class AskResponse(BaseModel):
    answer: str
    processing_time: float
    source: Optional[str] = 'llm'
    cached: Optional[bool] = False