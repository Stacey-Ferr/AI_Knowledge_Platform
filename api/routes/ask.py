from fastapi import APIRouter
from openai import OpenAI
from core.config import settings
from schemas.requests import AskRequest
from schemas.responses import AskResponse
from services.ask_service import ask
from core.logging import logger

router = APIRouter()

client = OpenAI(
    api_key=settings.GEMINI_API_KEY,
    base_url=settings.GEMINI_BASE_URL
)

@router.post("/ask", response_model=AskResponse)
async def query(request: AskRequest):
    return await ask(request.query)
