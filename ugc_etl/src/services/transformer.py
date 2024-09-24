import logging

from aiokafka import ConsumerRecord
from pydantic import ValidationError
from schemas.user_movies import UserMoviesSchema

logger = logging.getLogger(__name__)


def prepare_data(msgs: list[ConsumerRecord]) -> list[tuple]:
    result = []
    for msg in msgs:
        try:
            res = UserMoviesSchema.model_validate_json(msg.value)
            result.append(res.as_tuple)
        except ValidationError as e:
            logger.error(f"Msg format error. Err: {e}")
    return result
