from core.logging import logger
from models.responses import HealthResponse

def check_cache(cache_client):
    try:
        cache_result = cache_client.ping()
        print("Cache ping result: ", cache_result)
        logger.info("Cache service is Healthy.")
        return HealthResponse(**{ "service" : "Cache", "status" : "healthy"})
    except Exception as e:
        logger.error(f"Cache service is Unhealthy.\nException occured: {e}")
        return HealthResponse(**{ "service" : "Cache", "status" : "unhealthy"})