from fastapi import Depends
from cache.dependencies import get_cache
from dependencies.retrieval import (get_embedding_service, get_vector_service,
                                    get_bm25_service, get_reranker, 
                                    get_prompt_builder, get_openai_provider)                                    
from services.ask_service import AskService

def get_ask_service(
        cache_client = Depends(get_cache),
        embedding_service = Depends(get_embedding_service),
        vector_service = Depends(get_vector_service),
        bm25_service = Depends(get_bm25_service),
        reranker = Depends(get_reranker),
        prompt_builder = Depends(get_prompt_builder),
        openai_provider = Depends(get_openai_provider)):
    return AskService(cache_client, embedding_service, vector_service, bm25_service,
                     reranker, prompt_builder, openai_provider)