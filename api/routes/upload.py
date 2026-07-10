from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)
from schemas.responses import UploadResponse
from services.ingestion_service import IngestionService
from core.config import settings
from core.exceptions import UnsupportedFileException
from pathlib import Path
from dependencies.retrieval import get_bm25_service

ingestion_service = IngestionService()

router = APIRouter()

@router.post("/upload_file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), bm25_service = Depends(get_bm25_service)):
    """
    Checks if file type is supported, if supported the file is processed
    """
    extension = Path(file.filename).suffix.lstrip(".").lower()
    if extension not in settings.ALLOWED_FILE_TYPES:
        raise UnsupportedFileException("Unsupported file type", status_code=400)
    result = await ingestion_service.process_file(file, bm25_service)
    return UploadResponse(metadata=result.metadata)
