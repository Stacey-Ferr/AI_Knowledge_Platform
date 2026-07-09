from fastapi import APIRouter, Request, Depends
from openai import OpenAI
from core.config import settings
from schemas.requests import AskRequest
from schemas.responses import AskResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from dependencies.services import get_ask_service

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
async def ask_query(
        request: Request,
        question: AskRequest,
        ask_service = Depends(get_ask_service)
    ):
    return await ask_service.ask(question.query)