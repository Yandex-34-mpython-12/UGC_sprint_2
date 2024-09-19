import orjson
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


def orjson_dumps(v):
    return orjson.dumps(v, default=jsonable_encoder).decode()


class BaseOrjsonModel(BaseModel):
    class Config:
        ...


class BaseIdFullName(BaseOrjsonModel):
    uuid: str
    full_name: str
