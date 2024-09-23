import http
from functools import wraps
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.core.config import settings
from src.models.auth import AuthRequest, User, UserRole


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> User:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN,
                                detail='Invalid authorization code.')
        if not credentials.scheme == 'Bearer':
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED,
                                detail='Only Bearer token might be accepted')
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN,
                                detail='Invalid or expired token.')
        return User(**decoded_token)

    def parse_token(self, jwt_token: str) -> Optional[dict]:
        return self.decode_token(jwt_token)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            return jwt.decode(
                token, settings.jwt_secret_key,
                audience="fastapi-users:auth",
                algorithms=[settings.jwt_algorithm]
            )
        except Exception:
            return None


async def get_current_user_global(request: AuthRequest, user: User = Depends(JWTBearer())):
    request.custom_user = user


def roles_required(roles_list: list[UserRole]):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user: User = kwargs.get('request').custom_user
            if not user or user.role not in [x for x in roles_list]:
                raise HTTPException(
                    detail='This operation is forbidden for you',
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            return await function(*args, **kwargs)
        return wrapper
    return decorator
