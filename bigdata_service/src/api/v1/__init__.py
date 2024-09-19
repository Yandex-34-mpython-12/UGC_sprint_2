from fastapi import APIRouter
from src.core.config import settings

from .health import router as health_router
from .movies import router as movies_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)
router.include_router(health_router)
router.include_router(movies_router)
