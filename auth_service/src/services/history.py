from functools import lru_cache
from typing import Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.postgres import db_helper
from src.models import UserSignIn


class HistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_history(self, user_id: UUID, limit: int = 3, offset: int = 0) -> Sequence[UserSignIn]:
        query = select(UserSignIn).where(UserSignIn.user_id ==
                                         user_id).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()


@lru_cache()
def get_history_service(
    db: AsyncSession = Depends(db_helper.session_getter),
) -> HistoryService:
    return HistoryService(db=db)
