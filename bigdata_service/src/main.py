import logging
from contextlib import asynccontextmanager

import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from src.api import router as api_router
from src.core.config import settings
from src.core.logger import LOGGING, setup_root_logger
from src.middleware.request_log import RequestLogMiddleware
from src.services import kafka

setup_root_logger()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_startup
    kafka.kafka_producer = AIOKafkaProducer(
        bootstrap_servers=[settings.kafka.bootstrap_server],
    )
    await kafka.kafka_producer.start()

    yield

    # on_shutdown
    await kafka.kafka_producer.stop()

app = FastAPI(
    title='bigdata_service',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    root_path="/bigdata",
    lifespan=lifespan
)

app.add_middleware(RequestLogMiddleware)

app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=settings.run.log_level,
    )
