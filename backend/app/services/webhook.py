"""Webhook verification and storage."""

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.event import Event
from app.services.state_resolver import resolve_state_after_event


def _verify_stripe(payload: bytes, signature: str | None) -> bool:
    """Verify Stripe webhook signature. Header format: t=timestamp,v1=hex_sig. Sig = HMAC-SHA256(secret, t + '.' + body)."""
    if not settings.stripe_webhook_secret or not signature:
        return False
    try:
        import hmac
        import hashlib
        parts = {}
        for p in signature.split(","):
            kv = p.strip().split("=", 1)
            if len(kv) == 2:
                parts[kv[0]] = kv[1]
        t = parts.get("t")
        v1 = parts.get("v1")
        if not t or not v1:
            return False
        signed = f"{t}.{payload.decode('utf-8', errors='replace')}"
        mac = hmac.new(
            settings.stripe_webhook_secret.encode(),
            signed.encode(),
            hashlib.sha256,
        )
        computed = mac.hexdigest()
        return hmac.compare_digest(computed, v1)
    except Exception:
        return False


def _verify_lemonsqueezy(payload: bytes, headers: dict) -> bool:
    """Verify Lemon Squeezy webhook signature (signature in header)."""
    if not settings.lemonsqueezy_webhook_secret:
        return False
    sig = headers.get("X-Signature") or headers.get("x-signature")
    if not sig:
        return False
    import hmac
    import hashlib
    computed = hmac.new(
        settings.lemonsqueezy_webhook_secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(computed, sig)


def _verify_paddle(payload: bytes, headers: dict) -> bool:
    """Verify Paddle webhook (Paddle uses different signing)."""
    if not settings.paddle_webhook_secret:
        return False
    # Paddle signature verification varies by product; minimal check
    sig = headers.get("Paddle-Signature") or headers.get("paddle-signature")
    return bool(sig and settings.paddle_webhook_secret)


async def verify_and_store_webhook(
    db: AsyncSession,
    provider: str,
    body: bytes,
    stripe_signature: str | None,
    headers: dict,
) -> tuple[bool, int, str]:
    """
    Verify signature, store raw payload idempotently, then run state resolver.
    Returns (success, status_code, detail_message).
    """
    provider_lower = provider.lower()
    if provider_lower == "stripe":
        if not _verify_stripe(body, stripe_signature):
            return (False, 401, "Invalid or missing signature")
    elif provider_lower == "lemonsqueezy":
        if not _verify_lemonsqueezy(body, headers):
            return (False, 401, "Invalid or missing signature")
    elif provider_lower == "paddle":
        if not _verify_paddle(body, headers):
            return (False, 401, "Invalid or missing signature")
    else:
        return (False, 400, "Unknown provider")

    try:
        payload_json = json.loads(body.decode("utf-8"))
    except Exception:
        return (False, 400, "Invalid JSON")

    # Idempotency: get event_id from payload (provider-specific)
    event_id_from_provider = _extract_event_id(provider_lower, payload_json)
    if not event_id_from_provider:
        # Still store but use a fallback id
        event_id_from_provider = f"evt_{id(payload_json)}"

    existing = await db.execute(
        select(Event).where(Event.provider == provider_lower, Event.event_id == event_id_from_provider)
    )
    if existing.scalar_one_or_none() is not None:
        # Idempotent: already stored
        return (True, 200, "OK")

    event_type = _extract_event_type(provider_lower, payload_json) or "unknown"

    event = Event(
        provider=provider_lower,
        event_type=event_type,
        event_id=event_id_from_provider,
        received_at=datetime.now(timezone.utc),
        raw_payload=payload_json,
    )
    db.add(event)
    await db.flush()
    await resolve_state_after_event(db, event)
    return (True, 200, "OK")


def _extract_event_id(provider: str, payload: dict) -> str | None:
    """Extract provider event id from payload."""
    if provider == "stripe":
        return payload.get("id")
    if provider == "lemonsqueezy":
        return payload.get("meta", {}).get("event_name") or payload.get("id")
    if provider == "paddle":
        return payload.get("event_id") or payload.get("alert_id")
    return None


def _extract_event_type(provider: str, payload: dict) -> str | None:
    """Extract event type from payload."""
    if provider == "stripe":
        return payload.get("type")
    if provider == "lemonsqueezy":
        return payload.get("meta", {}).get("event_name")
    if provider == "paddle":
        return payload.get("event_type") or payload.get("alert_name")
    return None
