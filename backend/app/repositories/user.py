"""User, subscription, entitlement repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.subscription import Subscription
from app.models.entitlement import Entitlement
from app.schemas.users import EntitlementOut, SubscriptionOut


async def get_user_entitlements(db: AsyncSession, user_id: str) -> list[EntitlementOut] | None:
    """Return entitlements for user or None if user not found."""
    user = await db.get(User, user_id)
    if user is None:
        return None
    result = await db.execute(select(Entitlement).where(Entitlement.user_id == user_id))
    rows = result.scalars().all()
    return [EntitlementOut(user_id=user_id, feature_key=e.feature_key, enabled=e.enabled) for e in rows]


async def get_user_entitlement(db: AsyncSession, user_id: str, feature_key: str) -> EntitlementOut | None:
    """Return single entitlement or None."""
    result = await db.execute(
        select(Entitlement).where(Entitlement.user_id == user_id, Entitlement.feature_key == feature_key)
    )
    ent = result.scalar_one_or_none()
    if ent is None:
        return None
    return EntitlementOut(user_id=user_id, feature_key=ent.feature_key, enabled=ent.enabled)


async def get_user_subscription(db: AsyncSession, user_id: str) -> tuple[bool, SubscriptionOut | None]:
    """Return (user_found, subscription). subscription is None if user has no subscription."""
    user = await db.get(User, user_id)
    if user is None:
        return (False, None)
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    sub = result.scalar_one_or_none()
    if sub is None:
        return (True, None)
    return (
        True,
        SubscriptionOut(
            id=sub.id,
            plan_id=sub.plan_id,
            status=sub.status,
            started_at=sub.started_at,
            ended_at=sub.ended_at,
        ),
    )
