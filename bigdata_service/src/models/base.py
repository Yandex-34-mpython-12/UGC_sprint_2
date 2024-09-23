from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


class BaseOrjsonModel(BaseModel):
    class Config:
        ...


class Base(DeclarativeBase):
    __abstract__ = True
