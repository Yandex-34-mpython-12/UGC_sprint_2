from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str


class RoleRead(RoleBase):
    id: int


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass
