from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from src.api.v1.fastapi_users import current_active_superuser
from src.core.config import settings
from src.schemas import RoleCreate, RoleRead, RoleUpdate
from src.services.role import RoleService, role_service

router = APIRouter(
    prefix=settings.api.v1.roles,
    tags=["Roles"],
    dependencies=[Depends(current_active_superuser)]
)


@router.post('/create', status_code=HTTPStatus.OK, description='Create new role', response_model=RoleRead)
async def create_role(
    role_create: RoleCreate,
    role_svc: RoleService = Depends(role_service),
):
    try:
        role = await role_svc.create_role(role_create)
    except Exception:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Role is taken')
    return role


@router.get(
    '/list',
    status_code=HTTPStatus.OK,
    description='List Roles',
    response_model=List[RoleRead],
)
async def get_roles(
    role_svc: RoleService = Depends(role_service),
):
    return await role_svc.get_roles()


@router.delete(
    '/{role_id}',
    status_code=HTTPStatus.NO_CONTENT,
    description='Delete Roles',
)
async def delete_role(
    role_id: int,
    role_svc: RoleService = Depends(role_service),
) -> None:
    result = await role_svc.delete_role(role_id)

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Role not exist'
        )


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role(
        role_id: int,
        role_update: RoleUpdate,
        role_svc: RoleService = Depends(role_service),
):
    return await role_svc.update_role(role_id, role_update)
