from pydantic import BaseModel

class LLM_Config(BaseModel):
    provider: str
    model: str
    api_key: str
    base_url: str | None = None