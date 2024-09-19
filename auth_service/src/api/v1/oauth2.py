from fastapi import APIRouter, Request, Depends

from src.core.config import settings
from src.schemas import OAuthUser
from src.services.oauth import oauth, YandexOauth2, OAuth2Service

router = APIRouter(
    prefix=settings.api.v1.oauth,
    tags=["OAuth2"],
)

oauth2_svc = OAuth2Service(YandexOauth2())


@router.get("/login/{provider}")
async def login(request: Request, provider: str):
    redirect_uri = request.url_for('auth_callback', provider=provider)
    client = oauth.create_client(provider)
    return await client.authorize_redirect(request, redirect_uri)


@router.get('/callback/{provider}')
async def auth_callback(request: Request, provider: str):
    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)
    return token


@router.get("/protected")
async def need_yandex_oauth(user: OAuthUser = Depends(oauth2_svc)):
    return {"user": user}
