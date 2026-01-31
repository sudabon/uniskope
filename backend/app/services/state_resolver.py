"""State resolver: derive User, Subscription, Entitlement from events."""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.user import User
from app.models.subscription import Subscription
from app.models.entitlement import Entitlement
from app.models.state_transition import StateTransition


async def resolve_state_after_event(db: AsyncSession, event: Event) -> None:
    """Process a single new event and update User, Subscription, Entitlement, StateTransition."""
    provider = event.provider
    payload = event.raw_payload

    if provider == "stripe":
        await _apply_stripe_event(db, event, payload)
    elif provider == "lemonsqueezy":
        await _apply_lemonsqueezy_event(db, event, payload)
    elif provider == "paddle":
        await _apply_paddle_event(db, event, payload)
    # else: unknown provider, only event stored


async def _apply_stripe_event(db: AsyncSession, event: Event, payload: dict) -> None:
    """Map Stripe event to internal state."""
    typ = payload.get("type") or event.event_type
    data = payload.get("data", {})
    obj = data.get("object", {})

    if typ == "checkout.session.completed":
        customer_id = obj.get("customer") or obj.get("client_reference_id")
        if customer_id:
            user = await _get_or_create_user(db, customer_id, "stripe")
            await _record_transition(db, "user", user.id, None, user.status, event.id)

    elif typ in ("customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"):
        sub_id = obj.get("id")
        customer_id = obj.get("customer")
        if not customer_id:
            return
        user = await _get_or_create_user(db, customer_id, "stripe")
        status = _stripe_subscription_status(obj.get("status"))
        old_sub = await _get_latest_subscription(db, user.id)
        old_status = old_sub.status if old_sub else None

        sub_entity_id: str = user.id
        if typ == "customer.subscription.deleted" or status == "canceled":
            if old_sub:
                old_sub.status = "canceled"
                old_sub.ended_at = datetime.now(timezone.utc)
                sub_entity_id = old_sub.id
        else:
            if old_sub:
                old_sub.plan_id = obj.get("items", {}).get("data", [{}])[0].get("price", {}).get("id") or old_sub.plan_id
                old_sub.status = status
                sub_entity_id = old_sub.id
            else:
                sub = Subscription(
                    user_id=user.id,
                    plan_id=obj.get("items", {}).get("data", [{}])[0].get("price", {}).get("id") or "unknown",
                    status=status,
                    started_at=datetime.fromtimestamp(obj.get("start_date", 0), tz=timezone.utc) if obj.get("start_date") else None,
                    ended_at=None,
                )
                db.add(sub)
                await db.flush()
                sub_entity_id = sub.id
        await db.flush()
        await _record_transition(db, "subscription", sub_entity_id, old_status, status, event.id)
        await _sync_entitlements_for_user(db, user.id, status in ("active", "trialing"))

    # invoice.payment_failed, charge.refunded: optional handling
    elif typ == "invoice.payment_failed":
        customer_id = obj.get("customer")
        if customer_id:
            user = await _get_user_by_external(db, customer_id, "stripe")
            if user:
                sub = await _get_latest_subscription(db, user.id)
                if sub and sub.status == "active":
                    sub.status = "past_due"
                    await _record_transition(db, "subscription", sub.id, "active", "past_due", event.id)
                    await _sync_entitlements_for_user(db, user.id, False)


async def _get_or_create_user(db: AsyncSession, external_customer_id: str, provider: str) -> User:
    """Get or create user by external_customer_id and provider."""
    from sqlalchemy import select
    r = await db.execute(
        select(User).where(User.external_customer_id == external_customer_id, User.provider == provider)
    )
    user = r.scalar_one_or_none()
    if user is not None:
        return user
    user = User(
        external_customer_id=external_customer_id,
        provider=provider,
        status="active",
    )
    db.add(user)
    await db.flush()
    return user


async def _get_user_by_external(db: AsyncSession, external_customer_id: str, provider: str) -> User | None:
    """Get user by external_customer_id and provider."""
    from sqlalchemy import select
    r = await db.execute(
        select(User).where(User.external_customer_id == external_customer_id, User.provider == provider)
    )
    return r.scalar_one_or_none()


def _stripe_subscription_status(st: str | None) -> str:
    """Map Stripe subscription status to internal."""
    if not st:
        return "active"
    m = {"active": "active", "trialing": "trialing", "past_due": "past_due", "canceled": "canceled", "unpaid": "past_due"}
    return m.get(st, "active")


async def _get_latest_subscription(db: AsyncSession, user_id: str) -> Subscription | None:
    """Get latest subscription for user."""
    from sqlalchemy import select, desc
    r = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id).order_by(desc(Subscription.created_at)).limit(1)
    )
    return r.scalar_one_or_none()


async def _record_transition(
    db: AsyncSession,
    entity_type: str,
    entity_id: str,
    from_state: str | None,
    to_state: str,
    event_id: str,
) -> None:
    """Record state transition."""
    t = StateTransition(
        entity_type=entity_type,
        entity_id=entity_id,
        from_state=from_state,
        to_state=to_state,
        event_id=event_id,
    )
    db.add(t)


async def _sync_entitlements_for_user(db: AsyncSession, user_id: str, enabled: bool) -> None:
    """Set all entitlements for user to enabled (minimal: single default feature)."""
    from sqlalchemy import select
    r = await db.execute(select(Entitlement).where(Entitlement.user_id == user_id))
    existing = list(r.scalars().all())
    if existing:
        for e in existing:
            e.enabled = enabled
    else:
        ent = Entitlement(user_id=user_id, feature_key="default", enabled=enabled)
        db.add(ent)
    await db.flush()


async def _apply_lemonsqueezy_event(db: AsyncSession, event: Event, payload: dict) -> None:
    """Map Lemon Squeezy event to internal state (stub: store event only, minimal state)."""
    # Minimal: only event stored; state resolver can be extended later
    pass


async def _apply_paddle_event(db: AsyncSession, event: Event, payload: dict) -> None:
    """Map Paddle event to internal state (stub: store event only)."""
    pass
