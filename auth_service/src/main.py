from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis

from src.middleware.request_log import RequestLogMiddleware
from src.api import router as api_router
from src.core.config import settings
from src.core.logger import LOGGING, setup_root_logger
from src.core.tracer import configure_tracer
from src.db import redis
from starlette.middleware.sessions import SessionMiddleware


setup_root_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_startup
    redis.redis = Redis(host=settings.cache.host,
                        port=settings.cache.port, decode_responses=True)

    yield
    # on_shutdown
    await redis.redis.aclose()

app = FastAPI(
    title=settings.run.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    root_path="/auth"
)

app.include_router(api_router)

# OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.oauth.secret_key)
app.add_middleware(RequestLogMiddleware)

# Настраимаем Jaeger
if settings.jaeger.enable:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
        log_config=LOGGING,
        log_level=settings.run.log_level,
    )
