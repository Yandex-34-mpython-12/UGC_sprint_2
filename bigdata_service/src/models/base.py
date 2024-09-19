from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel


class BaseOrjsonModel(BaseModel):
    class Config:
        ...


class Base(DeclarativeBase):
    __abstract__ = True
