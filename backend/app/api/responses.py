"""Helpers that build the standard {"data": ...} / {"data": [...], "pagination": {...}} envelopes."""
from pydantic import BaseModel

from app.utils.pagination import PageParams, page_payload


def ok(schema: type[BaseModel], obj) -> dict:
    return {"data": schema.model_validate(obj)}


def paged(schema: type[BaseModel] | None, items: list, total: int, params: PageParams) -> dict:
    data = items if schema is None else [schema.model_validate(i) for i in items]
    return page_payload(data, total, params)


COMMON_ERRORS = {
    401: {"description": "Missing, invalid or expired token"},
    403: {"description": "Authenticated but not permitted for this role"},
}
