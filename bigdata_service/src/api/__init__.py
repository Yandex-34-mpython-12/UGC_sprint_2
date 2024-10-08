from fastapi import APIRouter, FastAPI
from src.core.config import settings

from .v1 import v1_router

api_router = APIRouter(
    prefix=settings.api.prefix,
)
api_router.include_router(v1_router)


router = APIRouter()
router.include_router(api_router)


def setup_routers(app: FastAPI):
    root_router = APIRouter()
    root_router.include_router(router)
    app.include_router(root_router)
