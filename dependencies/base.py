from services.embedding_service import OpenAIEmbeddingService
from services.vector_store_service import VectorStoreService
from services.tokenizer_service import Tokenizer
from services.bm25_service import Bm25Service
from services.reranking_service import RerankerService
from services.prompt_builder import PromptBuilder
from services.llm_provider import OpenAIProvider

embedding_service = OpenAIEmbeddingService()
vector_service = VectorStoreService()
tokenizer = Tokenizer()
bm25_service = Bm25Service(tokenizer)

reranker = RerankerService()
prompt_builder = PromptBuilder()
openai_provider = OpenAIProvider()

def get_embedding_service():
    return embedding_service

def get_vector_service():
    return vector_service

def get_tokenizer():
    return tokenizer

def get_bm25_service():
    return bm25_service

def get_reranker():
    return reranker

def get_prompt_builder():
    return prompt_builder

def get_openai_provider():
    return openai_provider