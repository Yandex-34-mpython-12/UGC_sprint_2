import uuid
from datetime import datetime

from fastapi_users_db_sqlalchemy import GUID, UUID_ID
from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserSignIn(Base):
    __tablename__ = 'user_sign_in'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'schema': 'users',
            'postgresql_partition_by': 'LIST (user_device_type)'
        }
    )

    id: Mapped[UUID_ID] = mapped_column(
        GUID, primary_key=True, default=uuid.uuid4, nullable=False)
    user_id: Mapped[UUID_ID] = mapped_column(ForeignKey("users.user.id"))
    logged_in_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user_agent: Mapped[str] = mapped_column()
    user_device_type: Mapped[str] = mapped_column(primary_key=True)

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logged_in_at}>'
