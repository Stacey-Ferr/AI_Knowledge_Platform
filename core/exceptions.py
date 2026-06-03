class RateLimitError(Exception):
    """
        Raised when the LLM provider returns a rate limit.
    """
    pass

class LLMTimeoutError(Exception):
    """
        Raised when the LLM request times out.
    """
    pass

class LLMServiceUnavailableError(Exception):
    """
        Raised when the LLM service is unavailable.
    """
    pass