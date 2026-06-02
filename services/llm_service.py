from openai import OpenAI
from models.responses import HealthResponse
from dotenv import load_dotenv
from core.logging import logger
from core.config import settings

load_dotenv()

client = OpenAI(
    api_key=settings.GEMINI_API_KEY,
    base_url=settings.GEMINI_BASE_URL
)

async def check_llm():
    try:
        models = client.models.list()
        logger.info("OpenAI service is Healthy")
        return HealthResponse(**{ "service" : "openai", "status" : "healthy"})
    except Exception as e:
        logger.error(f"OpenAI service is unhealthy.\nException occured: {e}")
        return HealthResponse(**{ "service" : "openai", "status" : "unhealthy"})