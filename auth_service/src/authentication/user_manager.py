import logging
import uuid
from typing import TYPE_CHECKING, Optional

from fastapi_users import BaseUserManager, UUIDIDMixin
from src.core.config import settings
from src.models.user import User
from src.utils.user_agent import get_type_from_user_agent

if TYPE_CHECKING:
    from fastapi import Request, Response

log = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def on_after_login(
            self,
            user: User,
            request: Optional["Request"] = None,
            response: Optional["Response"] = None,
    ):
        user_agent = request.headers.get("User-Agent")
        device_type = get_type_from_user_agent(user_agent)
        await self.user_db.create_sign_in_history(
            user_id=user.id,
            user_agent=user_agent,
            user_device_type=device_type
        )

    async def on_after_register(
        self,
        user: User,
        request: Optional["Request"] = None,
    ):
        log.warning(
            "User %r has registered.",
            user.id,
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        log.warning(
            "Verification requested for user %r. Verification token: %r",
            user.id,
            token,
        )

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        log.warning(
            "User %r has forgot their password. Reset token: %r",
            user.id,
            token,
        )
