"""User, subscription, entitlement schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EntitlementOut(BaseModel):
    """Single entitlement."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    feature_key: str
    enabled: bool


class EntitlementsOut(BaseModel):
    """List of entitlements for a user."""

    user_id: str
    entitlements: list[EntitlementOut]


class SubscriptionOut(BaseModel):
    """Subscription for a user."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    plan_id: str
    status: str
    started_at: datetime | None
    ended_at: datetime | None


class UserSubscriptionOut(BaseModel):
    """User subscription response (subscription can be null)."""

    user_id: str
    subscription: SubscriptionOut | None
