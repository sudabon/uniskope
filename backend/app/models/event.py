"""Event model - immutable webhook event log."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.state_transition import StateTransition


class Event(Base):
    """Immutable event record from webhook payloads."""

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("provider", "event_id", name="uq_events_provider_event_id"),
        Index("ix_events_received_at", "received_at"),
        Index("ix_events_provider_event_type", "provider", "event_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    state_transitions: Mapped[list["StateTransition"]] = relationship(
        "StateTransition", back_populates="event", foreign_keys="StateTransition.event_id"
    )
