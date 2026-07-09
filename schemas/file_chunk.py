from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class FileChunk(BaseModel):
    # Creates an 'id' automatically when creating a chunk
    id: UUID = Field(default_factory=uuid4)
    text: str
    document_id: str
    document_name: str
    page_numbers: list[int] | None = None
    section_title: list[str] | None = None
    chunk_index: int