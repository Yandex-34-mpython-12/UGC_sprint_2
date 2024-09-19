from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MovieStatus(Enum):
    in_progress = "in_progress"
    completed = "completed"


class UserMoviesSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    user_id: UUID
    movie_id: UUID
    progress: float
    status: MovieStatus
    last_watched: datetime

    @property
    def as_tuple(self):
        return (
            self.user_id,
            self.movie_id,
            self.progress,
            self.status,
            self.last_watched,
        )
