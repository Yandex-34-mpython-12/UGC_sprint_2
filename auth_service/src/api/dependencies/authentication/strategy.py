from src.authentication.strategy import JWTRedisStrategy
from src.core.config import settings


def get_jwt_strategy() -> JWTRedisStrategy:
    return JWTRedisStrategy(
        secret=settings.access_token.jwt_encode_secret,
        lifetime_seconds=settings.access_token.lifetime_seconds
    )
