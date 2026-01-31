"""Event repository."""

from datetime import datetime

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.schemas.events import EventOut


async def list_events(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    provider: str | None = None,
    event_type: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> tuple[list[EventOut], int]:
    """List events with filters and pagination. Returns (events, total_count)."""
    q = select(Event)
    count_q = select(func.count()).select_from(Event)

    if provider is not None:
        q = q.where(Event.provider == provider)
        count_q = count_q.where(Event.provider == provider)
    if event_type is not None:
        q = q.where(Event.event_type == event_type)
        count_q = count_q.where(Event.event_type == event_type)
    if since is not None:
        q = q.where(Event.received_at >= since)
        count_q = count_q.where(Event.received_at >= since)
    if until is not None:
        q = q.where(Event.received_at <= until)
        count_q = count_q.where(Event.received_at <= until)

    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    q = q.order_by(desc(Event.received_at)).limit(limit).offset(offset)
    result = await db.execute(q)
    rows = result.scalars().all()
    events = [
        EventOut(id=e.id, provider=e.provider, event_type=e.event_type, event_id=e.event_id, received_at=e.received_at, raw_payload=e.raw_payload)
        for e in rows
    ]
    return (events, total)
