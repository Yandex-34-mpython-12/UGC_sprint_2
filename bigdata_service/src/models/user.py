from enum import Enum
from uuid import UUID

from pydantic import Field

from .base import BaseOrjsonModel


class User(BaseOrjsonModel):
    uuid: UUID = Field(..., alias="sub")
    role: "UserRole" = Field(..., alias="role")


class UserRole(Enum):
    anonymous: str = 'anonymous'
    admin: str = 'admin'
    user: str = 'user'
    subscriber: str = 'subscriber'
