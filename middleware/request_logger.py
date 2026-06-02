from starlette.middleware.base import BaseHTTPMiddleware
from time import time
from core.logging import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        try:
            start = time()
            response = await call_next(request)
            duration = time() - start

            logger.info(f"{request.method}  {request.url.path}  {response.status_code}  {duration:.3f}s")
            return response

        except Exception as e:
            logger.exception(f"Exception occured: {e}")

