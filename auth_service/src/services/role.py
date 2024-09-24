from functools import lru_cache
from typing import Sequence

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.postgres import db_helper
from src.models import Role
from src.schemas import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_role(self, role_create: RoleCreate) -> Role:
        role = Role(**role_create.model_dump())
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_roles(self) -> Sequence[Role]:
        result = await self.db.scalars(select(Role))
        return result.all()

    async def update_role(self, role_id: int, role_update: RoleUpdate) -> Role:
        stmt = (
            update(Role)
            .where(Role.id == role_id)
            .values(**role_update.model_dump(exclude_unset=True))
            .returning(Role)
        )
        return await self.db.scalar(stmt)

    async def delete_role(self, role_id: int) -> bool:
        result = await self.db.execute(delete(Role).where(Role.id == role_id))
        await self.db.commit()
        return bool(result)


@lru_cache()
def role_service(
    db: AsyncSession = Depends(db_helper.session_getter),
) -> RoleService:
    return RoleService(db=db)
