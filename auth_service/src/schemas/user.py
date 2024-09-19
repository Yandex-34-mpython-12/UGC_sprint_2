import uuid
from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    role_id: Optional[int] = None


class UserCreate(schemas.BaseUserCreate):
    role_id: Optional[int] = None


class UserUpdate(schemas.BaseUserUpdate):
    role_id: Optional[int] = None


class OAuthUser(BaseModel):
    id: str
    login: str
    client_id: str
    psuid: str
