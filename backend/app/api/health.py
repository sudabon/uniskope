"""Health check endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check(response: Response, db: AsyncSession = Depends(get_db)) -> dict:
    """Return health status and database connectivity. Returns 503 when DB is disconnected."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        response.status_code = 503

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
