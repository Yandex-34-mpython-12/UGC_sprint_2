from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from src.db.postgres import db_helper
from src.models import User
from src.services.user import UserService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_users_db(
    session: Annotated[
        "AsyncSession",
        Depends(db_helper.session_getter),
    ],
):
    yield UserService(session, User)
