"""API key verification."""

from fastapi import Header, HTTPException

from app.core.config import settings


async def verify_api_key(
    authorization: str | None = Header(None),
) -> None:
    """Verify API key from Authorization header. If no API_KEY is configured, allow all (dev mode)."""
    if settings.api_key is None or settings.api_key == "":
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="API key required")
    token = authorization[7:].strip()
    if token != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
