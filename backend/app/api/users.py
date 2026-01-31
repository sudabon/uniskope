"""User and subscription/entitlement API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.auth import verify_api_key
from app.schemas.users import EntitlementOut, EntitlementsOut, SubscriptionOut, UserSubscriptionOut
from app.repositories.user import get_user_entitlements, get_user_subscription

router = APIRouter()


@router.get("/{user_id}/entitlements", response_model=EntitlementsOut)
async def get_entitlements(
    user_id: str,
    db=Depends(get_db),
    _: None = Depends(verify_api_key),
):
    """Get entitlements for a user."""
    entitlements = await get_user_entitlements(db, user_id)
    if entitlements is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return EntitlementsOut(user_id=user_id, entitlements=entitlements)


@router.get("/{user_id}/entitlements/{feature_key}", response_model=EntitlementOut)
async def get_entitlement(
    user_id: str,
    feature_key: str,
    db=Depends(get_db),
    _: None = Depends(verify_api_key),
):
    """Get a single entitlement for a user."""
    from app.repositories.user import get_user_entitlement

    ent = await get_user_entitlement(db, user_id, feature_key)
    if ent is None:
        raise HTTPException(status_code=404, detail="エンタイトルメントが見つかりません")
    return ent


@router.get("/{user_id}/subscription", response_model=UserSubscriptionOut)
async def get_subscription(
    user_id: str,
    db=Depends(get_db),
    _: None = Depends(verify_api_key),
):
    """Get subscription for a user."""
    found, sub = await get_user_subscription(db, user_id)
    if not found:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return UserSubscriptionOut(user_id=user_id, subscription=sub)
