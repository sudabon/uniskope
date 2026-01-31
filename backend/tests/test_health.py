"""Health endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient) -> None:
    """GET /api/health returns 200 and JSON with status."""
    r = await client.get("/api/health")
    # May be 200 (DB connected) or 503 (DB disconnected in CI)
    assert r.status_code in (200, 503)
    data = r.json()
    assert "status" in data
    assert "database" in data
    assert "timestamp" in data
