import logging
import sentry_sdk
from contextlib import asynccontextmanager

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from src.api.rate_limit import check_rate_limit
from src.api.v1 import auth, films, genres, health, persons
from src.core.config import settings
from src.core.logger import LOGGING, setup_root_logger
from src.core.tracer import configure_tracer
from src.db import elastic, redis
from src.middleware.request_log import RequestLogMiddleware

setup_root_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_startup
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[
            f'{settings.elastic_schema}://{settings.elastic_host}:{settings.elastic_port}']
    )
    yield
    # on_shutdown
    await redis.redis.aclose()
    await elastic.es.close()


sentry_sdk.init(
    dsn="https://3b658373696aeb1a2032d5b3f870caa6@o4508031233818624.ingest.de.sentry.io/4508036491182160",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


app = FastAPI(
    title=settings.run.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    root_path="/films"
)

app.add_middleware(RequestLogMiddleware)

# Set up Jaeger
if settings.enable_tracing:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)

dependencies = [
    Depends(auth.get_current_user_global),  # Global auth dependency
    Depends(check_rate_limit)  # Global rate limit dependency
]

app.include_router(
    films.router,
    prefix='/api/v1/films',
    tags=['films'],
    dependencies=dependencies
)

app.include_router(
    genres.router,
    prefix='/api/v1/genres',
    tags=['genres'],
    dependencies=dependencies
)

app.include_router(
    persons.router,
    prefix='/api/v1/persons',
    tags=['persons'],
    dependencies=dependencies
)

app.include_router(
    health.router,
    prefix='/api/health',
    tags=['health'],
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
