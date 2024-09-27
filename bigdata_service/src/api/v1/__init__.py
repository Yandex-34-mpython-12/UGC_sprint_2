from fastapi import APIRouter
from src.core.config import settings

from .health import router as health_router
from .movies import router as movies_router
from .posts import router as posts_router
from .comments import router as comments_router

v1_router = APIRouter(
    prefix=settings.api.v1.prefix,
)
v1_router.include_router(health_router)
v1_router.include_router(movies_router)
v1_router.include_router(posts_router)
v1_router.include_router(comments_router)
