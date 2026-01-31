"""StateTransition model - audit log for state changes."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.event import Event


class StateTransition(Base):
    """Record of state change for audit."""

    __tablename__ = "state_transitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    from_state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    to_state: Mapped[str] = mapped_column(String(64), nullable=False)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    transitioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    event: Mapped["Event"] = relationship("Event", back_populates="state_transitions")
