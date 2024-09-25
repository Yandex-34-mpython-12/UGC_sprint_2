import uuid
from abc import ABC, abstractmethod
from http import HTTPStatus

from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException, Request, status
from fastapi.security.utils import get_authorization_scheme_param
from httpx import AsyncClient
from src.api.dependencies.http_client import get_http_client
from src.core.config import settings
from src.schemas import OAuthUser

from src.core.context import ctx_request_id

oauth = OAuth()
oauth.register(
    name=settings.oauth.yandex.name,
    client_id=settings.oauth.yandex.client_id,
    client_secret=settings.oauth.yandex.client_secret,
    authorize_url=settings.oauth.yandex.authorize_url,
    authorize_params=None,
    access_token_url=settings.oauth.yandex.token_url,
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=settings.oauth.yandex.redirect_uri,
)


class BaseOAuthService(ABC):
    @abstractmethod
    async def get_user_info(self, client: AsyncClient, token: str) -> OAuthUser:
        pass


class YandexOauth2(BaseOAuthService):
    async def get_user_info(self, client: AsyncClient, token: str) -> OAuthUser:
        headers = self.get_headers(token)
        url = settings.oauth.yandex.user_info_url
        response = await client.get(url, headers=headers)
        if response.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "OAuth"},
            )
        data = response.json()
        return OAuthUser(**data)

    @staticmethod
    def get_headers(token: str) -> dict[str, str]:
        return {
            "Authorization": f"OAuth {token}",
            "X-Request-Id": ctx_request_id.get(uuid.uuid4()),
        }


class OAuth2Service:
    def __init__(self, service: BaseOAuthService):
        self.service = service

    async def __call__(self, request: Request, client: AsyncClient = Depends(get_http_client)) -> OAuthUser:
        authorization = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await self.service.get_user_info(client, token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
