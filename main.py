from fastapi import FastAPI
from api.routes.health import router as health_router
from api.routes.ask import router as ask_router
from middleware.request_logger import RequestLoggingMiddleware

app = FastAPI()

app.include_router(health_router)
app.include_router(ask_router)

app.add_middleware(RequestLoggingMiddleware)