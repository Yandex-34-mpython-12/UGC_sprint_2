from fastapi_users.authentication import BearerTransport
from src.core.config import settings

bearer_transport = BearerTransport(
    tokenUrl=settings.api.bearer_token_url,
)
