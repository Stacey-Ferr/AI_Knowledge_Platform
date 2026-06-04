from fastapi import APIRouter, Request, Depends
from openai import OpenAI
from core.config import settings
from schemas.requests import AskRequest
from schemas.responses import AskResponse
from services.ask_service import ask
from core.logging import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from cache.dependencies import get_cache

router = APIRouter()

client = OpenAI(
    api_key=settings.GEMINI_API_KEY,
    base_url=settings.GEMINI_BASE_URL
)

limiter = Limiter(
    key_func = get_remote_address
)

@router.post("/ask", response_model=AskResponse)
@limiter.limit("10/hour")
async def query(
        request: Request,
        question: AskRequest,
        cache_client = Depends(get_cache)
    ):
    return await ask(question.query, cache_client)