# fastapi-tortoiseorm

This project is a step toward a configuration-based list view inspired by Django REST Framework, with built-in pagination, search, filtering, and ordering capabilities.

## Main reference

If you want to understand the full flow, start with:

`app/main.py` -> `async def get_tournaments(request: Request, pagination: PaginationDep):`

This endpoint is the primary reference for how pagination plus filter/sort/search are wired together.

## Run locally

```bash
make dev
```

API base URL: `http://127.0.0.1:8000`  
Interactive docs: `http://127.0.0.1:8000/docs`

## `GET /tournaments`

Returns a paginated list of tournaments, including nested events.

### Query params

- `limit` (int, default `20`, min `1`, max `100`): page size
- `offset` (int, default `0`): pagination offset
- `name` (str): exact filter on `Tournament.name`
- `events__name` (str): exact filter on related `Event.name`
- `search` (str): search across `name` and `events__name`
- `ordering` (str): comma-separated fields from `id,name,created`; prefix with `-` for descending (example: `-id`)

### Examples

List first page:

```bash
curl "http://127.0.0.1:8000/tournaments?limit=20&offset=0"
```

Filter by tournament name:

```bash
curl "http://127.0.0.1:8000/tournaments?name=tourney%20A"
```

Filter by related event name:

```bash
curl "http://127.0.0.1:8000/tournaments?events__name=event%20A"
```

Search and sort descending by id:

```bash
curl "http://127.0.0.1:8000/tournaments?search=tourney&ordering=-id"
```

### Response shape

```json
{
  "total": 3,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "id": 1,
      "name": "tourney A",
      "created": "2026-02-21T12:34:56.000000Z",
      "events": [
        {
          "id": 1,
          "name": "event A",
          "modified": "2026-02-21T12:34:56.000000Z",
          "prize": "1000.00"
        }
      ]
    }
  ]
}
```
