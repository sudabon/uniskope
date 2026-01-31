"""Dashboard repository: aggregated stats and lists."""

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.subscription import Subscription
from app.models.state_transition import StateTransition


async def get_active_users_count(db: AsyncSession) -> int:
    """Return count of users with status active."""
    r = await db.execute(select(func.count()).select_from(User).where(User.status == "active"))
    return r.scalar() or 0


async def get_active_subscriptions_list(
    db: AsyncSession,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Return list of active subscriptions with user info."""
    q = (
        select(Subscription, User.external_customer_id, User.provider)
        .join(User, Subscription.user_id == User.id)
        .where(Subscription.status.in_(["active", "trialing"]))
        .order_by(desc(Subscription.created_at))
        .limit(limit)
        .offset(offset)
    )
    r = await db.execute(q)
    rows = r.all()
    return [
        {
            "id": sub.id,
            "user_id": sub.user_id,
            "external_customer_id": ext_id,
            "provider": prov,
            "plan_id": sub.plan_id,
            "status": sub.status,
            "started_at": sub.started_at.isoformat() if sub.started_at else None,
            "created_at": sub.created_at.isoformat() if sub.created_at else None,
        }
        for sub, ext_id, prov in rows
    ]


async def get_state_transitions_list(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    entity_type: str | None = None,
) -> list[dict]:
    """Return state transitions for audit log."""
    q = select(StateTransition).order_by(desc(StateTransition.transitioned_at)).limit(limit).offset(offset)
    if entity_type:
        q = q.where(StateTransition.entity_type == entity_type)
    r = await db.execute(q)
    rows = r.scalars().all()
    return [
        {
            "id": t.id,
            "entity_type": t.entity_type,
            "entity_id": t.entity_id,
            "from_state": t.from_state,
            "to_state": t.to_state,
            "event_id": t.event_id,
            "transitioned_at": t.transitioned_at.isoformat() if t.transitioned_at else None,
        }
        for t in rows
    ]
