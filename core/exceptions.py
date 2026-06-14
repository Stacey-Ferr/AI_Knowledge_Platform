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

class FileException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class EmptyFileException(FileException):
    pass

class UnsupportedFileException(FileException):
    pass

class CorruptFileException(FileException):
    pass