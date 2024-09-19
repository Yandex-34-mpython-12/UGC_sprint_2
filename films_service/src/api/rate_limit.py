import datetime

from fastapi import Depends, HTTPException, status
from src.core.config import settings
from src.db.redis import AsyncRedisCache, get_redis
from src.models.auth import AuthRequest


async def check_rate_limit(request: AuthRequest, redis: AsyncRedisCache = Depends(get_redis)) -> None:
    user = request.custom_user

    pipe = await redis.pipeline()
    now = datetime.datetime.now()
    key = f'{user.uuid}:{now.minute}'

    await pipe.incr(key, 1)
    await pipe.expire(key, 59)

    result = await pipe.execute()
    request_number = result[0]
    if request_number > settings.request_limit_per_minute:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
