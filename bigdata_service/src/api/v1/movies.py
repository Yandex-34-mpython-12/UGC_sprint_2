import json

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends
from src.core.config import settings
from src.models import User
from src.schemas import MovieProgressUpdate
from src.services.kafka import get_kafka_producer

from .auth import get_current_user_global

router = APIRouter(
    prefix="/movies",
    tags=["Movies"],
)


@router.post("/update_progress")
async def update_progress(
    progress_update: MovieProgressUpdate,
    user: User = Depends(get_current_user_global),
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer)
):
    kafka_message = {
        "user_id": str(user.uuid),
        "movie_id": str(progress_update.movie_id),
        "progress": progress_update.progress,
        "status": progress_update.status,
        "last_watched": progress_update.last_watched.strftime("%Y-%m-%d %H:%M:%S")
    }
    # Convert the dictionary to a JSON string and then encode it to bytes
    message_bytes = json.dumps(kafka_message).encode('utf-8')

    # Send the message to Kafka
    await kafka_producer.send_and_wait(settings.kafka.topic, message_bytes)

    return {"status": "Message sent", "message": kafka_message}
