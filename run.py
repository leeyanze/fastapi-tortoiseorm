import asyncio
import json

import requests
from tortoise import Tortoise

from app.models import Event, Team, Tournament
from app.settings import TORTOISE_ORM


def print_json(data) -> None:
    print(json.dumps(data, indent=2, sort_keys=True, default=str))


def get_tournaments(search: str | None = None) -> None:
    url = "http://127.0.0.1:8000/tournaments"
    params = {"limit": 20, "offset": 0}
    if search:
        params["search"] = search

    response = requests.get(url, params=params, timeout=10)
    print(response.status_code)
    payload = response.json()
    print_json(payload)
    print(
        {
            "limit": payload.get("limit"),
            "offset": payload.get("offset"),
            "search": search,
        }
    )
    response.raise_for_status()


def get_events() -> None:
    url = "http://127.0.0.1:8000/events"
    response = requests.get(url, timeout=10)
    print(response.status_code)
    print_json(response.json())
    response.raise_for_status()


def get_events_rf() -> None:
    url = "http://127.0.0.1:8000/events_rf"
    response = requests.get(url, timeout=10)
    print(response.status_code)
    print_json(response.json())
    response.raise_for_status()


def get_tournaments_gt() -> None:
    url = "http://127.0.0.1:8000/tournaments_gt"
    response = requests.get(url, timeout=10)
    print(response.status_code)
    print_json(response.json())
    response.raise_for_status()


async def seeddb() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        # Clear current data before reseeding.
        conn = Tortoise.get_connection("default")
        await conn.execute_query("DELETE FROM event_team")
        await Event.all().delete()
        await Team.all().delete()
        await Tournament.all().delete()

        tournaments = []
        for name in ["tourney A", "tourney B", "tourney C"]:
            tournaments.append(await Tournament.create(name=name))

        teams = []
        for name in ["team A", "team B", "team C"]:
            teams.append(await Team.create(name=name))

        events = []
        for idx, name in enumerate(["event A", "event B", "event C"]):
            event = await Event.create(
                name=name,
                tournament=tournaments[idx],
                prize=f"{(idx + 1) * 1000:.2f}",
            )
            await event.participants.add(teams[idx])
            events.append(event)

        print(
            f"Seed complete: {len(tournaments)} tournaments, {len(teams)} teams, {len(events)} events"
        )
    finally:
        await Tortoise.close_connections()


def main() -> None:
    import sys

    command = sys.argv[1] if len(sys.argv) > 1 else "list"
    if command == "seed":
        asyncio.run(seeddb())
        return
    if command == "list":
        search = sys.argv[2] if len(sys.argv) > 2 else None
        get_tournaments(search)
        return
    if command == "search":
        if len(sys.argv) < 3:
            raise SystemExit("Usage: python run.py search <search>")
        get_tournaments(sys.argv[2])
        return
    if command == "events":
        get_events()
        return
    if command == "events-rf":
        get_events_rf()
        return
    if command == "tournaments-gt":
        get_tournaments_gt()
        return
    raise SystemExit(
        "Usage: python run.py [seed|list [search]|search <search>|events|events-rf|tournaments-gt]"
    )


if __name__ == "__main__":
    main()
