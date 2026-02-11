from pydantic import ConfigDict
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models import Event, Tournament
from app.pagination import make_page_model

TournamentBase_PYDANTIC = pydantic_model_creator(
    Tournament,
    name="TournamentBase_PYDANTIC",
    include=("id", "name", "created"),
)
EventNested_PYDANTIC = pydantic_model_creator(
    Event,
    name="EventNested_PYDANTIC",
    include=("id", "name", "modified", "prize"),
)


class TournamentList_PYDANTIC(TournamentBase_PYDANTIC):
    model_config = ConfigDict(from_attributes=True)
    events: list[EventNested_PYDANTIC]


TournamentIn_PYDANTIC = pydantic_model_creator(
    Tournament, name="TournamentIn", exclude_readonly=True
)
TournamentPage_PYDANTIC = make_page_model(
    TournamentList_PYDANTIC, "TournamentPage_PYDANTIC"
)
