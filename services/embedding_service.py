from typing import Protocol
from openai import OpenAI
from core.config import settings

class EmbeddingService(Protocol):

    def embed(self, text: str) -> list[float]:
        ...
    
    def embed_batch(self, text: list[str]) -> list[list[float]]:
        ...

class OpenAIEmbeddingService:
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )
    
    # Embeds a single line
    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model = settings.EMBEDDING_MODEL,
            input = text
        )
        return response.data[0].embedding

    # Embeds a list of strings in one go
    def embed_batch(self, text:list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model = settings.EMBEDDING_MODEL,
            input = text
        )
        return [item.embedding for item in response.data]