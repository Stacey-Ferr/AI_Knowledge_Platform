from core.logging import logger
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

class RetrievalService:
    def __init__(self, embedding_service, vector_service, bm25_service, reranker):
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.bm25_service = bm25_service
        self.reranker = reranker
        self.tracer = trace.get_tracer("retrieval_service")

    def retrieve(self, query: str) -> list[dict]:
        """
            Retrieving all the relevant chunks of data.
            First we create an embedding of the user query and search the vector database
            for the closest vectors. This is more of a semantic search.
            We also use BM25 to perform sparse retrieval. This does a similarity check
            against the chunks using a keyword search.
            Once we get the chunks from the qdrant vector database and from BM25 we merge
            the results and remove duplicates.
            Finally we rerank all the merged chunks to produce the most relevant chunks
            that will later be passed on to the LLM.
        """
        with self.tracer.start_as_current_span("embedding.generate") as embedding_span:
            embedding_span.set_attribute("embedding.model", "text-embedding-3-small")
            query_embedding = self.embedding_service.embed(query)
        with self.tracer.start_as_current_span("retrieval.hybrid_search") as retrieval_span:
            retrieval_span.set_attribute("retrieval.strategy", "hybrid")
            retrieval_span.set_attribute("retrieval.vector_top_k", 10)
            retrieval_span.set_attribute("retrieval.bm25_top_k", 5)
            retrieval_span.set_attribute("retrieval.reranking", True)
            retrieval_span.set_attribute("retrieval.final_top_k", 3)
            try:
                with self.tracer.start_as_current_span("qdrant.search") as dense_search_span:
                    dense_search_span.set_attribute("retrieval.strategy", "vector")
                    dense_search_span.set_attribute("retrieval.top_k", 10)
                    qdrant_matches = self.vector_service.search(query_embedding)

                with self.tracer.start_as_current_span("bm25.search") as sparse_search_span:
                    sparse_search_span.set_attribute("retrieval.strategy", "bm25")
                    sparse_search_span.set_attribute("retrieval.top_k", 5)
                    bm25_matches = self.bm25_service.retrieval(query)

                merged_matches = {}
                # Adding an id field to each of the qdrant points since the payload does not have this data.
                for match in qdrant_matches.points:
                    merged_matches[match.id] = {
                                                    **match.payload,
                                                    "id": match.id,
                                                }
                for match in bm25_matches:
                    merged_matches[match["id"]] = match

                with self.tracer.start_as_current_span("reranker") as reranker_span:
                    reranker_span.set_attribute("reranker.strategy", "cross-encoder")
                    reranker_span.set_attribute("reranker.top_k", 3)
                    reranker_span.set_attribute("reranker.candidates", len(merged_matches))
                    relevant_matches = self.reranker.rerank(query, merged_matches)
                return relevant_matches
            except Exception as e:
                logger.exception("Retrieval failed")
                raise