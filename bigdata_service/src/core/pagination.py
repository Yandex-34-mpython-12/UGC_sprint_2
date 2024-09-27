from typing import TypeVar

from fastapi import Query
from fastapi_pagination import Page, Params
from fastapi_pagination.customization import CustomizedPage, UseParams

T = TypeVar("T")


class CustomParams(Params):
    page: int = Query(1, ge=1, description="Pagination page number")
    size: int = Query(10, ge=1, le=100, description="Pagination page size")


PaginatedPage = CustomizedPage[
    Page[T],
    UseParams(CustomParams),
]
