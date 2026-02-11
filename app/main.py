import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from tortoise import Tortoise

from app.models import Event, Tournament
from app.pagination import (
    CommonListDependencies,
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
async def get_tournaments(common_list_dependencies: CommonListDependencies):
    return await paginate_queryset_with_mapper(
        Tournament.all().prefetch_related("events"),
        **common_list_dependencies.model_dump(),
        mapper=lambda tournament: TournamentList_PYDANTIC.model_validate(
            tournament, from_attributes=True
        ),
    )


@app.post("/tournaments", response_model=TournamentList_PYDANTIC)
async def create_tournament(payload: TournamentIn_PYDANTIC):
    tournament = await Tournament.create(**payload.model_dump(exclude_unset=True))
    return await TournamentList_PYDANTIC.from_tortoise_orm(tournament)


@app.get("/tournaments_gt", response_model=TournamentPage_PYDANTIC)
async def get_tournaments_gt(common_list_dependencies: CommonListDependencies):
    return await paginate_queryset_with_mapper(
        Tournament.objects.with_prize_gt().prefetch_related("events"),
        **common_list_dependencies.model_dump(),
        mapper=lambda tournament: TournamentList_PYDANTIC.model_validate(
            tournament, from_attributes=True
        ),
    )


@app.get("/events", response_model=EventPage_PYDANTIC)
async def get_events(common_list_dependencies: CommonListDependencies):
    return await paginate_queryset_with_mapper(
        Event.all().prefetch_related("tournament", "participants"),
        **common_list_dependencies.model_dump(),
        mapper=lambda event: EventList_PYDANTIC.model_validate(
            event, from_attributes=True
        ),
    )


@app.get("/events_rf", response_model=EVENTS_RF_CONFIG.page_schema)
async def get_events_rf(common_list_dependencies: CommonListDependencies):
    return await paginate_from_config(EVENTS_RF_CONFIG, common_list_dependencies)
