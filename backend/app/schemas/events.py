"""Event schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventOut(BaseModel):
    """Single event."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    provider: str
    event_type: str
    event_id: str
    received_at: datetime
    raw_payload: dict


class EventsListOut(BaseModel):
    """Paginated events list."""

    data: list[EventOut]
    pagination: dict
