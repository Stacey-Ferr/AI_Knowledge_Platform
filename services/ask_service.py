from schemas.responses import AskResponse
import hashlib
import json
from core.logging import logger

class AskService:

    def __init__(self, cache_client, embedding_service, vector_service, bm25_service,
                     reranker, prompt_builder, openai_provider):
        self.cache_client = cache_client
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.bm25_service = bm25_service
        self.reranker = reranker
        self.prompt_builder = prompt_builder
        self.openai_provider = openai_provider

    def _retrieve(self, query: str) -> list[dict]:
        """
            Retrieving all the relevant chunks of data.
            First we create an embedding of the user query and search the vector database for the
            closest vectors. This is more of a semantic search.
            We also use BM25 to perform sparse retrieval. This does a similarity check against the
            chunks using a keyword search.
            Once we get the chunks from the qdrant vector database and from BM25 we merge the results
            and remove duplicates.
            Finally we rerank all the merged chunks to produce the most relevant chunks that will later be
            passed on to the LLM.
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

    async def ask(self, query: str) -> AskResponse:
        """
            User enters a query, if the query exists in the cache, the cached response is given back.
            If the response is from cache, the response will have cached as 'True' and source as 'cached'.
            If the response is not cached the '_retrieve' function above is called.
            The prompt to be passed to the LLM is built and then sent to the OpenAI LLM.
            The response from the LLM is then cached.
        """
        cache_key = ("ask:" + hashlib.sha256(query.encode()).hexdigest())
        cached_answer = self.cache_client.get(cache_key)

        if cached_answer:
            payload = json.loads(cached_answer)
            payload['cached'] = True
            payload['source'] = "cache"
            return AskResponse(**payload)

        relevant_matches = self._retrieve(query)

        system_prompt, user_prompt = self.prompt_builder.build_prompt(query, relevant_matches)

        response = await self.openai_provider.generate(system_prompt, user_prompt)
        self.cache_client.set(
            cache_key,
            json.dumps(response.model_dump()),
            ex=3600
        )
        return response