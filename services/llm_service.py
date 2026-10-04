from schemas.responses import HealthResponse
from core.logging import logger
from dependencies.llm_client import llm_client

async def check_llm():
    try:
        await llm_client.models.list()
        logger.info("OpenAI service is Healthy")
        return HealthResponse(**{ "service" : "openai", "status" : "healthy"})
    except Exception as e:
        logger.error(f"OpenAI service is unhealthy.\nException occured: {e}")
        return HealthResponse(**{ "service" : "openai", "status" : "unhealthy"})