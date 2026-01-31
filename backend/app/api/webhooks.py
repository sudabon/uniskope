"""Webhook ingest endpoints."""

from fastapi import APIRouter, Depends, Request, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.webhook import verify_and_store_webhook

router = APIRouter()


@router.post("/{provider}")
async def receive_webhook(
    request: Request,
    provider: str,
    db: AsyncSession = Depends(get_db),
):
    """Receive webhook from payment provider. Signature verification and idempotent storage."""
    body = await request.body()
    # Stripe sends signature in header
    stripe_sig = request.headers.get("stripe-signature")
    # Lemon Squeezy / Paddle may use different headers; we pass raw for verification inside service
    headers = dict(request.headers) if request.headers else {}

    ok, status_code, message = await verify_and_store_webhook(db, provider, body, stripe_sig, headers)
    if not ok:
        raise HTTPException(status_code=status_code, detail=message)
    return {"received": True}
