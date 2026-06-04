from services.llm_provider import OpenAIProvider
from schemas.responses import AskResponse
import hashlib
from time import time
import json

async def ask(query: str, cache_client):
    cache_key = ("ask:" + hashlib.sha256(query.encode()).hexdigest())
    cached_answer = cache_client.get(cache_key)

    if cached_answer:
        payload = json.loads(cached_answer)
        payload['cached'] = True
        payload['source'] = "cache"
        return AskResponse(**payload)

    provider = OpenAIProvider()
    response = provider.generate(query)
    cache_client.set(
        cache_key,
        json.dumps(response.model_dump()),
        ex=3600
    )
    return response