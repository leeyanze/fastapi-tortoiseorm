import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from tortoise import Tortoise

from app.filter_sort_search import filter_sort_search_queryset
from app.models import Event, Tournament
from app.pagination import (
    PaginationParams,
    get_pagination_params,
    ListEndpointConfig,
    paginate_from_config,
    paginate_queryset_with_mapper,
)
from app.schemas import (
    EventList_PYDANTIC,
    EventPage_PYDANTIC,
    TournamentIn_PYDANTIC,
    TournamentList_PYDANTIC,
    TournamentPage_PYDANTIC,
)
from app.settings import TORTOISE_ORM


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        yield
    finally:
        await Tortoise.close_connections()


app = FastAPI(title="FastTortoise", lifespan=lifespan)
logger = logging.getLogger(__name__)

PaginationDep = Annotated[PaginationParams, Depends(get_pagination_params)]

EVENTS_RF_CONFIG = ListEndpointConfig(
    queryset_factory=lambda: Event.all().prefetch_related("tournament", "participants"),
    item_schema=EventList_PYDANTIC,
    page_schema=EventPage_PYDANTIC,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/tournaments", response_model=TournamentPage_PYDANTIC)
async def get_tournaments(request: Request, pagination: PaginationDep):
    '''
    Example endpoint demonstrating the use of filter_sort_search_queryset.
    '''
    filterset_fields = ["name", "events__name"]
    search_fields = ["name", "events__name"]
    ordering_fields = ["id", "name", "created"]

    queryset = filter_sort_search_queryset(
        Tournament.all().prefetch_related("events"),
        request,
        filterset_fields=filterset_fields,
        search_fields=search_fields,
        ordering_fields=ordering_fields,
    )
    return await paginate_queryset_with_mapper(
        queryset,
        **pagination.model_dump(),
        mapper=lambda tournament: TournamentList_PYDANTIC.model_validate(
            tournament, from_attributes=True
        ),
    )


@app.post("/tournaments", response_model=TournamentList_PYDANTIC)
async def create_tournament(payload: TournamentIn_PYDANTIC):
    tournament = await Tournament.create(**payload.model_dump(exclude_unset=True))
    return await TournamentList_PYDANTIC.from_tortoise_orm(tournament)


@app.get("/tournaments_gt", response_model=TournamentPage_PYDANTIC)
async def get_tournaments_gt(pagination: PaginationDep):
    return await paginate_queryset_with_mapper(
        Tournament.objects.with_prize_gt().prefetch_related("events"),
        **pagination.model_dump(),
        mapper=lambda tournament: TournamentList_PYDANTIC.model_validate(
            tournament, from_attributes=True
        ),
    )


@app.get("/events", response_model=EventPage_PYDANTIC)
async def get_events(pagination: PaginationDep):
    return await paginate_queryset_with_mapper(
        Event.all().prefetch_related("tournament", "participants"),
        **pagination.model_dump(),
        mapper=lambda event: EventList_PYDANTIC.model_validate(
            event, from_attributes=True
        ),
    )


@app.get("/events_rf", response_model=EVENTS_RF_CONFIG.page_schema)
async def get_events_rf(pagination: PaginationDep):
    return await paginate_from_config(EVENTS_RF_CONFIG, pagination)
