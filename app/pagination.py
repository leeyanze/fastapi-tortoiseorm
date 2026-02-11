from typing import Annotated, Callable
from dataclasses import dataclass

from fastapi import Depends, Query
from pydantic import BaseModel, create_model


class PaginationParams(BaseModel):
    limit: int
    offset: int


def get_pagination_params(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


CommonListDependencies = Annotated[PaginationParams, Depends(get_pagination_params)]


def make_page_model(item_model: type[BaseModel], name: str) -> type[BaseModel]:
    return create_model(
        name,
        total=(int, ...),
        limit=(int, ...),
        offset=(int, ...),
        items=(list[item_model], ...),
    )


async def paginate_queryset(
    queryset, pydantic_model, *, limit: int, offset: int
) -> dict:
    total = await queryset.count()
    items = await pydantic_model.from_queryset(queryset.offset(offset).limit(limit))
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


async def paginate_queryset_with_mapper(
    queryset, *, limit: int, offset: int, mapper
) -> dict:
    total = await queryset.count()
    rows = await queryset.offset(offset).limit(limit)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [mapper(row) for row in rows],
    }


@dataclass(frozen=True)
class ListEndpointConfig:
    queryset_factory: Callable
    item_schema: type[BaseModel]
    page_schema: type[BaseModel]
    serializer: Callable | None = None


def orm_serializer(schema: type[BaseModel]):
    return lambda obj: schema.model_validate(obj, from_attributes=True)


async def paginate_from_config(
    config: ListEndpointConfig, params: PaginationParams
) -> dict:
    serializer = config.serializer or orm_serializer(config.item_schema)
    return await paginate_queryset_with_mapper(
        config.queryset_factory(),
        limit=params.limit,
        offset=params.offset,
        mapper=serializer,
    )
