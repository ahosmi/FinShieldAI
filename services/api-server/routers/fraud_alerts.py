"""FinShield AI — Fraud Alerts Router"""

from fastapi import APIRouter, Depends, Query
from services.redis_service import RedisService, get_redis
from services.postgres_service import PostgresService, get_postgres

router = APIRouter()


@router.get("")
async def list_alerts(
    limit: int = Query(20, ge=1, le=100),
    redis: RedisService = Depends(get_redis),
    pg: PostgresService = Depends(get_postgres),
):
    """Return most recent fraud alerts from PostgreSQL."""
    alerts = await pg.fetch_recent_alerts(limit)
    return {"alerts": alerts, "count": len(alerts)}


@router.get("/live")
async def live_alerts(
    limit: int = Query(20, ge=1, le=50),
    redis: RedisService = Depends(get_redis),
):
    """Return live alerts cached in Redis (sub-ms latency)."""
    alerts = await redis.get_recent_alerts(limit)
    return {"alerts": alerts, "count": len(alerts)}


@router.get("/stats")
async def alert_stats(pg: PostgresService = Depends(get_postgres)):
    """Dashboard KPI stats."""
    stats = await pg.fetch_dashboard_stats()
    return stats


@router.get("/suspicious-users")
async def suspicious_users(
    limit: int = Query(10, ge=1, le=50),
    redis: RedisService = Depends(get_redis),
):
    """Top suspicious users ranked by risk score (from Redis sorted set)."""
    users = await redis.get_top_suspicious(limit)
    return {"users": users}


@router.get("/{transaction_id}")
async def get_alert(
    transaction_id: str,
    pg: PostgresService = Depends(get_postgres),
):
    alert = await pg.fetch_alert_by_txn(transaction_id)
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(404, f"Alert not found for {transaction_id}")
    return alert
