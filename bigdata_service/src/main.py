import logging
from contextlib import asynccontextmanager

import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from motor.motor_asyncio import AsyncIOMotorClient
from src.api import setup_routers
from src.core.config import settings
from src.core.logger import LOGGING, setup_root_logger
from src.db import init_db, mongo
from src.middleware.request_log import RequestLogMiddleware
from src.db import kafka

setup_root_logger()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    kafka.kafka_producer = AIOKafkaProducer(
        bootstrap_servers=[settings.kafka.bootstrap_server],
    )
    await kafka.kafka_producer.start()
    mongo.mongo_client = AsyncIOMotorClient(str(settings.mongo.mongodb_uri))
    await init_db.init(client=mongo.mongo_client)

    yield

    await kafka.kafka_producer.stop()
    mongo.mongo_client.close()


def create_app():
    application = FastAPI(
        lifespan=lifespan,
        title="bigdata_service",
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
        root_path="/bigdata",
        description="Bigdata Service",
        version="0.1.0",
    )

    setup_routers(application)
    add_pagination(application)

    return application


app = create_app()
app.add_middleware(RequestLogMiddleware)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=settings.run.log_level,
    )
