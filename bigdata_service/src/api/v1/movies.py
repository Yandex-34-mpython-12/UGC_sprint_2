from fastapi import APIRouter, Depends
from src.models.auth import User
from src.schemas.movie import MovieProgressUpdate
from src.services.movie import MovieService, get_movie_service

from .auth import get_current_user_global

router = APIRouter(
    prefix="/movies",
    tags=["Movies"],
)


@router.post("/update_progress")
async def update_progress(
    progress_update: MovieProgressUpdate,
    user: User = Depends(get_current_user_global),
    movie_svc: MovieService = Depends(get_movie_service),
) -> dict:
    return await movie_svc.update_movie_progress(
        user_id=user.uuid,
        progress_update=progress_update,
    )
