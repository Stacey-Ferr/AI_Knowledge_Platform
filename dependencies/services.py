from services.embedding_service import OpenAIEmbeddingService
from services.vector_store_service import VectorStoreService
from services.tokenizer_service import Tokenizer
from services.bm25_service import Bm25Service
from fastapi import Depends
from cache.dependencies import get_cache
from dependencies.retrieval import (get_reranker, get_prompt_builder, get_openai_provider)
from services.ask_service import AskService
from services.ingestion_service import IngestionService

embedding_service = OpenAIEmbeddingService()
vector_service = VectorStoreService()
tokenizer = Tokenizer()
bm25_service = Bm25Service(tokenizer)

def get_embedding_service():
    return embedding_service

def get_vector_service():
    return vector_service

def get_tokenizer():
    return tokenizer

def get_bm25_service():
    return bm25_service

def get_ask_service(
                        cache_client = Depends(get_cache),
                        embedding_service = Depends(get_embedding_service),
                        vector_service = Depends(get_vector_service),
                        bm25_service = Depends(get_bm25_service),
                        reranker = Depends(get_reranker),
                        prompt_builder = Depends(get_prompt_builder),
                        openai_provider = Depends(get_openai_provider)
                    ):
    return AskService(cache_client = cache_client, embedding_service = embedding_service,
                      vector_service = vector_service, bm25_service = bm25_service,
                     reranker = reranker, prompt_builder = prompt_builder,
                     openai_provider = openai_provider)

def get_ingestion_service(
                            embedding_service = Depends(get_embedding_service),
                            vector_service = Depends(get_vector_service),
                            bm25_service = Depends(get_bm25_service)
                        ):
    return IngestionService(embedding_service = embedding_service, vector_service = vector_service,
                            bm25_service = bm25_service)