from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)
from schemas.responses import UploadResponse
from core.config import settings
from core.exceptions import UnsupportedFileException
from pathlib import Path
from dependencies.services import get_ingestion_service

router = APIRouter()

@router.post("/upload_file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), ingestion_service = Depends(get_ingestion_service)):
    """
    Checks if file type is supported, if supported the file is processed
    """
    extension = Path(file.filename).suffix.lstrip(".").lower()
    if extension not in settings.ALLOWED_FILE_TYPES:
        raise UnsupportedFileException("Unsupported file type", status_code=400)
    result = await ingestion_service.process_file(file)
    return UploadResponse(metadata=result.metadata)
