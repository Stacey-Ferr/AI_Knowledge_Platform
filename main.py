from fastapi import FastAPI
from api.routes.health import router as health_router
from api.routes.ask import router as ask_router
from api.routes.upload import router as upload_router
from middleware.request_logger import RequestLoggingMiddleware
from fastapi.responses import JSONResponse
from core.exceptions import FileException

app = FastAPI()

app.include_router(health_router)
app.include_router(ask_router)
app.include_router(upload_router)

app.add_middleware(RequestLoggingMiddleware)

@app.exception_handler(FileException)
async def file_exception_handler(request, exc):
    return JSONResponse(
        status_code = exc.status_code,
        content = {
            "detail" : exc.message
        }
    )