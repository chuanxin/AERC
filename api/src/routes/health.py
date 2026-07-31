"""External health-check endpoint — no authentication required.

Provides a lightweight probe for load balancers and external monitoring
systems (UptimeRobot, cloudflared health checks, etc.). Returns only a
status summary; never exposes internal details, versions, or error traces.

Two tiers:
  - Caddy layer `/health` — instant HTTP-level probe (no backend dependency)
  - FastAPI `/health` — deep check including database connectivity
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

logger = logging.getLogger("api.health")

router = APIRouter(tags=["Health"])


@router.get("/health", include_in_schema=False)
async def health_check() -> dict[str, Any]:
    """External health-check endpoint.

    Returns a minimal status payload. No authentication required.
    Never exposes versions, environment variables, or error details.
    """
    result: dict[str, Any] = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        # Lightweight query — verifies connection + read permission.
        # Uses raw execute to avoid Tortoise model overhead.
        start = time.monotonic()
        from tortoise import connections
        db = connections.get("default")
        await db.execute_query("SELECT 1")
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        result["db"] = {"status": "connected", "latency_ms": latency_ms}
    except Exception as exc:
        logger.error("Health check — database failure: %s", exc)
        result["db"] = {"status": "error"}
        result["status"] = "degraded"

    return result