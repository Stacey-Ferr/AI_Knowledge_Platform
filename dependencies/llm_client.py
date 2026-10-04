from core.config import settings
from openai import AsyncOpenAI

active_llm_config = settings.active_llm

if active_llm_config.base_url:
    llm_client = AsyncOpenAI(
                            api_key = active_llm_config.api_key,
                            base_url = active_llm_config.base_url
                        )
else:
    llm_client = AsyncOpenAI(
                            api_key = active_llm_config.api_key
                        )
