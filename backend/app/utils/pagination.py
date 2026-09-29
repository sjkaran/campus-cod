from dataclasses import dataclass

from fastapi import Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

MAX_PAGE_SIZE = 100


@dataclass(frozen=True)
class PageParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def page_params(
    page: int = Query(1, ge=1, description="1-based page number"),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE, description=f"Max {MAX_PAGE_SIZE}"),
) -> PageParams:
    return PageParams(page=page, page_size=page_size)


def paginate(db: Session, stmt, params: PageParams, *, scalars: bool = True):
    """Run `stmt` with LIMIT/OFFSET and a separate COUNT. Returns (items, total)."""
    total = db.execute(select(func.count()).select_from(stmt.order_by(None).subquery())).scalar_one()
    result = db.execute(stmt.limit(params.page_size).offset(params.offset))
    items = result.scalars().all() if scalars else result.all()
    return items, total


def page_payload(items: list, total: int, params: PageParams) -> dict:
    return {
        "data": items,
        "pagination": {"page": params.page, "page_size": params.page_size, "total": total},
    }
