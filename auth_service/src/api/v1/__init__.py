from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from src.core.config import settings

from .auth import router as auth_router
from .health import router as health_router
from .oauth2 import router as oauth2_router
from .roles import router as roles_router
from .users import router as users_router

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[Depends(http_bearer)],
)
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(roles_router)
router.include_router(oauth2_router)
