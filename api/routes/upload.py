from fastapi import (
    APIRouter,
    UploadFile,
    File
)
from schemas.responses import UploadResponse
from services.ingestion_service import IngestionService
from core.config import settings
from core.exceptions import UnsupportedFileException
from pathlib import Path

ingestion_service = IngestionService()

router = APIRouter()

@router.post("/upload_file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Checks if file type is supported, if supported the file is processed
    """
    extension = Path(file.filename).suffix.lstrip(".").lower()
    # extension = file.filename.split(".")[-1].lower()
    if extension not in settings.ALLOWED_FILE_TYPES:
        raise UnsupportedFileException("Unsupported file type", status_code=400)
    result = await ingestion_service.process_file(file)
    return UploadResponse(metadata=result.metadata)
