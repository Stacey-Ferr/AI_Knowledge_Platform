from schemas.responses import AskResponse
import hashlib
import json

class AskService:

    def __init__(self, cache_client, agent):
        self.cache_client = cache_client
        self.agent = agent

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

        response = await self.agent.run(query)
        self.cache_client.set(
            cache_key,
            json.dumps(response.model_dump()),
            ex=3600
        )
        return response