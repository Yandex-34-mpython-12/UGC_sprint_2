from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class MovieStatus(Enum):
    in_progress = "in_progress"
    completed = "completed"


class MovieProgressUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    movie_id: UUID
    status: MovieStatus
    progress: float
    last_watched: datetime

