from pydantic import BaseModel

class HealthResponse(BaseModel):
    service: str
    status: str

class AskResponse(BaseModel):
    answer: str
    processing_time: float