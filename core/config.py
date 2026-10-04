from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from schemas.llm_config import LLM_Config

class Settings(BaseSettings):
    """
        Application configuration settings
    """

    #-----------------------------------------------------------------
    # APP SETTINGS
    #-----------------------------------------------------------------
    APP_NAME: str = "AI Knowledge Platform"
    ENVIRONMENT: str
    DEBUG: bool = True


    #-----------------------------------------------------------------
    # SERVER SETTINGS
    #-----------------------------------------------------------------
    HOST: str = "127.0.0.1"
    PORT: int = 8000


    #-----------------------------------------------------------------
    # DATABASE
    #-----------------------------------------------------------------
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20


    #-----------------------------------------------------------------
    # REDIS / CACHE
    #-----------------------------------------------------------------
    REDIS_HOST: str
    REDIS_PORT: str


    #-----------------------------------------------------------------
    # OPENAI SERVICE
    #-----------------------------------------------------------------
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_MODEL_DIMENSIONS: int = 1536


    #-----------------------------------------------------------------
    # GEMINI SERVICE
    #-----------------------------------------------------------------
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"


    #-----------------------------------------------------------------
    # ACTIVE LLM
    #-----------------------------------------------------------------
    LLM_PROVIDER: str


    #-----------------------------------------------------------------
    # CORS
    #-----------------------------------------------------------------
    BACKEND_CORS_ORIGINS: list[str] = ["http://127.0.0.1:8000"]


    #-----------------------------------------------------------------
    # LOGGING
    #-----------------------------------------------------------------
    LOG_LEVEL: str


    #-----------------------------------------------------------------
    # FILE UPLOAD SETTINGS
    #-----------------------------------------------------------------
    MAX_FILE_SIZE_MB: int = 20

    ALLOWED_FILE_TYPES: list[str] = [
        "pdf",
        "txt",
        "docx",
        "md"
    ]


    #-----------------------------------------------------------------
    # PYDANTIC SETTINGS CONFIG
    #-----------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive = True,
        extra = "ignore"
    )

    @property
    def active_llm(self) -> LLM_Config:
        providers = {
            "gemini" : LLM_Config(
                provider = "gemini",
                model = self.GEMINI_MODEL,
                api_key = self.GEMINI_API_KEY,
                base_url = self.GEMINI_BASE_URL
            ),
            "openai" : LLM_Config(
                provider = "openai",
                model = self.OPENAI_MODEL,
                api_key=self.OPENAI_API_KEY,
                base_url=None
            )
        }

        try:
            return providers[self.LLM_PROVIDER]
        except KeyError:
            raise ValueError(f"Unsupported LLM provider: {self.LLM_PROVIDER}")


# Creates a single cached Settings object
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Global Settings Instance
settings = get_settings()
print("Config loaded!")