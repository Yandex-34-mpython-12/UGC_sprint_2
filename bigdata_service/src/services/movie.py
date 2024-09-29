import json
from functools import lru_cache
from typing import Any
from uuid import UUID

from aiokafka import AIOKafkaProducer
from fastapi import Depends
from src.core.config import settings
from src.db.kafka import get_kafka_producer
from src.schemas.movie import MovieProgressUpdate


class MovieService:
    def __init__(self, kafka_producer: AIOKafkaProducer):
        self.kafka_producer = kafka_producer

    async def update_movie_progress(
            self, user_id: str | UUID, progress_update: MovieProgressUpdate
    ) -> dict[str, Any]:
        kafka_message = {
            "user_id": str(user_id),
            "movie_id": str(progress_update.movie_id),
            "progress": progress_update.progress,
            "status": progress_update.status,
            "last_watched": progress_update.last_watched.strftime("%Y-%m-%d %H:%M:%S")
        }
        message_bytes = json.dumps(kafka_message).encode('utf-8')
        await self.kafka_producer.send_and_wait(settings.kafka.topic, message_bytes)
        return {"status": "Message sent", "message": kafka_message}


@lru_cache()
def get_movie_service(
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
) -> MovieService:
    return MovieService(kafka_producer=kafka_producer)
