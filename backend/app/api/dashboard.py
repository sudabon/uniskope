"""Dashboard read-only API: stats, subscriptions list, state transitions."""

from fastapi import APIRouter, Depends, Query

from app.core.database import get_db
from app.core.auth import verify_api_key
from app.repositories.dashboard import get_active_users_count, get_active_subscriptions_list, get_state_transitions_list

router = APIRouter()


@router.get("/stats")
async def get_stats(
    db=Depends(get_db),
    _: None = Depends(verify_api_key),
):
    """Return active users count and active subscriptions count."""
    active_users = await get_active_users_count(db)
    active_subs = await get_active_subscriptions_list(db, limit=10_000)
    return {"active_users": active_users, "active_subscriptions": len(active_subs)}


@router.get("/subscriptions")
async def get_subscriptions_list(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    _: None = Depends(verify_api_key),
):
    """Return list of active subscriptions for dashboard."""
    items = await get_active_subscriptions_list(db, limit=limit, offset=offset)
    return {"data": items}


@router.get("/state-transitions")
async def get_state_transitions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    entity_type: str | None = None,
    db=Depends(get_db),
    _: None = Depends(verify_api_key),
):
    """Return state transitions for audit log."""
    items = await get_state_transitions_list(db, limit=limit, offset=offset, entity_type=entity_type)
    return {"data": items}
