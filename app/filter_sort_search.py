import shlex
from datetime import date, datetime, time
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, Request
from tortoise.expressions import Q


def _strip_search_prefix(field: str) -> str:
    return field[1:] if field[:1] in {"^", "=", "$", "@"} else field


def _search_lookup(field: str) -> str:
    prefix = field[:1]
    if prefix == "^":
        return "istartswith"
    if prefix == "=":
        return "iexact"
    if prefix == "$":
        return "iregex"
    if prefix == "@":
        return "search"
    return "icontains"


def _search_terms(value: str) -> list[str]:
    """Split search input into terms after removing null bytes for query safety."""
    cleaned = value.replace("\x00", "")
    try:
        terms = shlex.split(cleaned)
    except ValueError:
        terms = cleaned.split()
    return [term.strip(",") for term in terms if term.strip(",")]


def _resolve_field_for_path(model, field_path: str):
    """Resolve a Django-style '__' field path to the final Tortoise model field."""
    current_model = model
    field = None
    for part in field_path.split("__"):
        if current_model is None:
            return None
        field = current_model._meta.fields_map.get(part)
        if field is None:
            return None
        current_model = getattr(field, "related_model", None)
    return field


def _coerce_filter_value(queryset, field: str, raw_value: str):
    """Cast query-string filter values to the target model field's Python type."""
    model = getattr(queryset, "model", None)
    model_field = _resolve_field_for_path(model, field)
    if model_field is None:
        return raw_value

    field_type = type(model_field).__name__

    if field_type in {"IntField", "BigIntField", "SmallIntField"}:
        return int(raw_value)
    if field_type == "FloatField":
        return float(raw_value)
    if field_type == "DecimalField":
        return Decimal(raw_value)
    if field_type == "BooleanField":
        normalized = raw_value.strip().lower()
        if normalized in {"1", "true", "t", "yes", "y"}:
            return True
        if normalized in {"0", "false", "f", "no", "n"}:
            return False
        raise ValueError("Expected a boolean value.")
    if field_type == "DatetimeField":
        return datetime.fromisoformat(raw_value)
    if field_type == "DateField":
        return date.fromisoformat(raw_value)
    if field_type == "TimeField":
        return time.fromisoformat(raw_value)
    if field_type == "UUIDField":
        return UUID(raw_value)

    return raw_value


def _apply_filtering(queryset, params, filterset_fields: Sequence[str]) -> tuple:
    needs_distinct = False
    for field in filterset_fields:
        raw_value = params.get(field)
        if raw_value is None or raw_value == "":
            continue

        try:
            value = _coerce_filter_value(queryset, field, raw_value)
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid value for filter '{field}': {raw_value!r}",
            ) from exc

        queryset = queryset.filter(**{field: value})
        if "__" in field:
            needs_distinct = True
    return queryset, needs_distinct


def _apply_search(
    queryset, params, search_fields: Sequence[str], needs_distinct: bool
) -> tuple:
    search = params.get("search")
    if not search or not search_fields:
        return queryset, needs_distinct

    terms = _search_terms(search)
    if not terms:
        return queryset, needs_distinct

    search_query = None
    for term in terms:
        term_query = Q()
        for field in search_fields:
            base_field = _strip_search_prefix(field)
            lookup = _search_lookup(field)
            term_query |= Q(**{f"{base_field}__{lookup}": term})
            if "__" in base_field:
                needs_distinct = True
        search_query = term_query if search_query is None else search_query & term_query

    if search_query is not None:
        queryset = queryset.filter(search_query)
    return queryset, needs_distinct


def _apply_ordering(queryset, params, ordering_fields: Sequence[str]):
    ordering = params.get("ordering")
    if not ordering or not ordering_fields:
        return queryset

    allowed = set(ordering_fields)
    order_by_fields = []
    for field in ordering.split(","):
        field = field.strip()
        if not field:
            continue
        normalized = field[1:] if field.startswith("-") else field
        if normalized in allowed:
            order_by_fields.append(field)

    if order_by_fields:
        queryset = queryset.order_by(*order_by_fields)
    return queryset


def filter_sort_search_queryset(
    queryset,
    request: Request,
    *,
    filterset_fields: Sequence[str],
    search_fields: Sequence[str],
    ordering_fields: Sequence[str],
):
    params = request.query_params
    queryset, needs_distinct = _apply_filtering(queryset, params, filterset_fields)
    queryset, needs_distinct = _apply_search(
        queryset, params, search_fields, needs_distinct
    )

    if needs_distinct:
        queryset = queryset.distinct()

    queryset = _apply_ordering(queryset, params, ordering_fields)
    return queryset
