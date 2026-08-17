from core.logging import logger

class RetrievalService:
    def __init__(self, embedding_service, vector_service, bm25_service, reranker):
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.bm25_service = bm25_service
        self.reranker = reranker

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
        try:
            query_embedding = self.embedding_service.embed(query)
            qdrant_matches = self.vector_service.search(query_embedding)

            merged_matches = {}
            # Adding an id field to each of the qdrant points since the payload does not have this data.
            for match in qdrant_matches.points:
                merged_matches[match.id] = {
                                                **match.payload,
                                                "id": match.id,
                                            }

            bm25_matches = self.bm25_service.retrieval(query)
            for match in bm25_matches:
                merged_matches[match["id"]] = match
            relevant_matches = self.reranker.rerank(query, merged_matches)
            return relevant_matches
        except Exception as e:
            logger.exception("Retrieval failed")
            raise