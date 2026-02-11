from pydantic import ConfigDict
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models import Event, Team, Tournament
from app.pagination import make_page_model

EventBase_PYDANTIC = pydantic_model_creator(
    Event,
    name="EventBase_PYDANTIC",
    include=("id", "name", "modified", "prize"),
)
TournamentNested_PYDANTIC = pydantic_model_creator(
    Tournament, name="TournamentNested_PYDANTIC"
)
TeamNested_PYDANTIC = pydantic_model_creator(Team, name="TeamNested_PYDANTIC")


class EventList_PYDANTIC(EventBase_PYDANTIC):
    model_config = ConfigDict(from_attributes=True)
    tournament: TournamentNested_PYDANTIC
    participants: list[TeamNested_PYDANTIC]


EventPage_PYDANTIC = make_page_model(EventList_PYDANTIC, "EventPage_PYDANTIC")

