from services.llm_provider import OpenAIProvider

async def ask(query: str):
    provider = OpenAIProvider()
    return provider.generate(query)