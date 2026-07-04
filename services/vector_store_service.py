from services.embedding_service import OpenAIEmbeddingService
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from core.config import settings
from uuid import uuid4
from datetime import datetime
from zoneinfo import ZoneInfo
from core.logging import logger
from core.exceptions import VectorStoreException

class VectorStoreService:
    """
        Used to create vectors from the chunks
    """
    def __init__(self):
        """
            Sets up a QdrantClient connection
            Checks if the collection 'Documents' already exists, if it doesn't the collection is created
        """
        self.client = QdrantClient(host="localhost", port=6333, timeout=600)
        self.collection_name = "Documents"
        self.batch_size = 250

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                    collection_name = self.collection_name,
                    vectors_config = VectorParams(
                            size=settings.EMBEDDING_MODEL_DIMENSIONS,
                            distance=Distance.COSINE
                        )
                )
    
    def create_point_structures(self, final_chunks):
        """
            Creates PointStruct objects for each chunk and chunk embedding
        """
        points = []
        embedding = OpenAIEmbeddingService()
        text = [chunk.text for chunk in final_chunks]
        chunk_embeddings = []

        for index in range(0, len(text), self.batch_size):
            batch = text[index : index+self.batch_size]
            chunk_embeddings.extend(embedding.embed_batch(batch))
        
        for chunk, embedding in zip(final_chunks, chunk_embeddings):
            points.append(
                PointStruct(
                    id = str(uuid4()),
                    vector = embedding,
                    payload = {
                        "text": chunk.text,
                        "document_id" : chunk.document_id,
                        "document_name": chunk.document_name,
                        "page_numbers": chunk.page_numbers,
                        "section_title": chunk.section_title,
                        "chunk_index": chunk.chunk_index,
                        "uploaded_at": datetime.now(ZoneInfo("Asia/Kolkata"))
                    }
                ))
        return points

    def upsert(self, points):
        """
            Adds each of the PointStruct objects to the qdrant vector store
        """
        operation_info = self.client.upsert(
            collection_name = self.collection_name,
            points = points,
            wait = True
        )

        logger.info(
            "Upsert completed: operation_id=%s, status=%s",
            operation_info.operation_id,
            operation_info.status,
        )

        if operation_info.status != "completed":
            raise VectorStoreException("Failed to upsert vectors into Qdrant.")
    
    def search():
        pass