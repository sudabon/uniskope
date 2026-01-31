"""Events API endpoint."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.core.database import get_db
from app.core.auth import verify_api_key
from app.schemas.events import EventOut, EventsListOut
from app.repositories.event import list_events

router = APIRouter()


@router.get("", response_model=EventsListOut)
async def get_events(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    provider: str | None = None,
    event_type: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    db=Depends(get_db),
    _: None = Depends(verify_api_key),
):
    """List events with optional filters and pagination."""
    events, total = await list_events(
        db, limit=limit, offset=offset, provider=provider, event_type=event_type, since=since, until=until
    )
    return EventsListOut(
        data=events,
        pagination={
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(events) < total,
        },
    )
