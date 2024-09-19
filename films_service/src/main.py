import logging
from contextlib import asynccontextmanager

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis

from src.api.rate_limit import check_rate_limit
from src.api.v1 import films, genres, health, persons, auth
from src.core.config import settings
from src.core.logger import LOGGING
from src.core.tracer import configure_tracer
from src.db import elastic, redis


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


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    root_path="/films"
)

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
