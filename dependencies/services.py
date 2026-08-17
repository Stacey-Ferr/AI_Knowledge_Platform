from fastapi import Depends
from cache.dependencies import get_cache
from dependencies.agentic_ai import get_agent
from services.ask_service import AskService
from dependencies.base import get_embedding_service, get_vector_service, get_bm25_service
from services.ingestion_service import IngestionService

def get_ask_service(cache_client = Depends(get_cache), agent = Depends(get_agent)):
    return AskService(cache_client = cache_client, agent = agent)

def get_ingestion_service(
                            embedding_service = Depends(get_embedding_service),
                            vector_service = Depends(get_vector_service),
                            bm25_service = Depends(get_bm25_service)
                        ):
    return IngestionService(embedding_service = embedding_service, vector_service = vector_service,
                            bm25_service = bm25_service)