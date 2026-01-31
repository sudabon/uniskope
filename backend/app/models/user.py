"""User model - derived from events."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    """User (customer) derived from webhook events."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_customer_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()"))

    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="user")
    entitlements: Mapped[list["Entitlement"]] = relationship("Entitlement", back_populates="user")


from app.models.subscription import Subscription  # noqa: E402
from app.models.entitlement import Entitlement  # noqa: E402
