from fastapi_users.authentication import AuthenticationBackend
from src.authentication.transport import bearer_transport

from .strategy import get_jwt_strategy

authentication_backend = AuthenticationBackend(
    name="jwt-redis",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
