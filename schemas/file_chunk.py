from pydantic import BaseModel

class FileChunk(BaseModel):
    text: str
    document_id: str
    document_name: str
    page_numbers: list[int] | None = None
    section_title: list[str] | None = None
    chunk_index: int