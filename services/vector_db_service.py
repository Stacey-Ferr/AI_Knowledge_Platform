from qdrant_client import QdrantClient
from core.logging import logger
from models.responses import HealthResponse

async def check_vector_db():
    try:
        client = QdrantClient(host="localhost", port=6333, timeout=600)
        result = client.get_collections()
        logger.info(f"Vector db service is Healthy.\nResult: {result}")
        return HealthResponse(**{ "service" : "Qdrant db", "status" : "healthy"})
    except Exception as e:
        logger.error(f"Vector db service is unhealthy.\nException {e} occurred")
        return HealthResponse(**{ "service" : "Qdrant db", "status" : "unhealthy"})