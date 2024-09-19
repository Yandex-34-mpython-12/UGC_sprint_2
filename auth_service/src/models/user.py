from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import UserSchemaMixin


class User(UserSchemaMixin, SQLAlchemyBaseUserTableUUID, Base):
    role_id: Mapped[int] = mapped_column(ForeignKey("users.roles.id"), nullable=True)

    role: Mapped["Role"] = relationship(back_populates="users", lazy="selectin")

    def __repr__(self) -> str:
        return f'<User: {self.email}>'


class Role(UserSchemaMixin, Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="role", lazy="selectin")
