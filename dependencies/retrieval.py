from services.reranking_service import RerankerService
from services.prompt_builder import PromptBuilder
from services.llm_provider import OpenAIProvider

reranker = RerankerService()
prompt_builder = PromptBuilder()
openai_provider = OpenAIProvider()

def get_reranker():
    return reranker

def get_prompt_builder():
    return prompt_builder

def get_openai_provider():
    return openai_provider