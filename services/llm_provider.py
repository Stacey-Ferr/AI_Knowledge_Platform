from services.interfaces import BaseLLMProvider
from openai import (
        OpenAI,
        RateLimitError as LLMRateLimitError,
        APITimeoutError,
        APIConnectionError,
        APIStatusError
    )
from core.config import settings
from time import time
from schemas.responses import AskResponse
from tenacity import (
                        retry,
                        stop_after_attempt,
                        wait_exponential,
                        retry_if_exception_type
                    )
from core.exceptions import (
    RateLimitError,
    LLMTimeoutError,
    LLMServiceUnavailableError
)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.client = OpenAI(
                        api_key=settings.GEMINI_API_KEY,
                        base_url=settings.GEMINI_BASE_URL
                    )

    @retry(
        stop = stop_after_attempt(3),
        wait = wait_exponential(
            multiplier = 10,
            min = 10,
            max = 60
        ),
        retry = retry_if_exception_type(
            (
                RateLimitError,
                LLMTimeoutError,
                LLMServiceUnavailableError
            )
        )
    )
    async def generate(self, system_prompt: str, user_prompt: str):
        """
            Uses the system prompt and user prompt passed to the function to answer the user query.
            Retries if the execution fails due to a RateLimitError, LLMTimeoutError, or an
            LLMServiceUnavailableError. Maximum 3 re-attempts on failure.
        """
        try:
            start_time = time()
            response = self.client.chat.completions.create(
                model = "gemini-2.5-flash",
                messages=[
                            {
                                "role" : "system",
                                "content" : system_prompt
                            },
                            {
                                "role" : "user",
                                "content" : user_prompt
                            }
                        ]
            )
            total_time = time() - start_time
            return AskResponse(**{"answer":response.choices[0].message.content, "processing_time":total_time})
        except LLMRateLimitError:
            raise RateLimitError("OpenAI rate limit exceeded")
        except APITimeoutError:
            raise LLMTimeoutError("OpenAI Request timed out")
        except APIConnectionError:
            raise LLMServiceUnavailableError("Could not connect to OpenAI")
        except APIStatusError as e:
            print(f"Status code: {e.status_code}")
            raise LLMServiceUnavailableError("OpenAI returned an error")