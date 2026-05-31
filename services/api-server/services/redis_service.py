"""FinShield AI — Redis Service"""

import json
import logging
import os
from typing import List, Optional

import redis.asyncio as aioredis

logger = logging.getLogger("redis-service")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

_instance: Optional["RedisService"] = None


class RedisService:
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    async def connect(self):
        self.client = aioredis.from_url(REDIS_URL, decode_responses=True)
        await self.client.ping()
        logger.info("Redis connected")

    async def disconnect(self):
        if self.client:
            await self.client.close()

    # ── Alerts ────────────────────────────────────────────────────────

    async def set_alert(self, txn_id: str, alert: dict, ttl: int = 3600):
        await self.client.setex(f"alert:{txn_id}", ttl, json.dumps(alert))
        # Keep a sorted set for fast top-N queries, scored by risk_score
        score = alert.get("risk_score", 0)
        await self.client.zadd("alerts:recent", {txn_id: score})
        await self.client.expire("alerts:recent", 3600)

    async def get_recent_alerts(self, limit: int = 20) -> List[dict]:
        txn_ids = await self.client.zrevrange("alerts:recent", 0, limit - 1)
        alerts = []
        for tid in txn_ids:
            raw = await self.client.get(f"alert:{tid}")
            if raw:
                alerts.append(json.loads(raw))
        return alerts

    # ── User Risk ─────────────────────────────────────────────────────

    async def set_user_risk(self, user_id: str, score: float, ttl: int = 600):
        await self.client.setex(f"risk:{user_id}", ttl, str(score))

    async def get_user_risk(self, user_id: str) -> Optional[float]:
        val = await self.client.get(f"risk:{user_id}")
        return float(val) if val else None

    # ── Suspicious Users ──────────────────────────────────────────────

    async def add_to_active_suspicious(self, user_id: str, score: float):
        await self.client.zadd("active_suspicious", {user_id: score})
        await self.client.expire("active_suspicious", 3600)

    async def get_top_suspicious(self, limit: int = 10) -> List[dict]:
        results = await self.client.zrevrange(
            "active_suspicious", 0, limit - 1, withscores=True
        )
        return [{"user_id": uid, "risk_score": round(score, 2)} for uid, score in results]

    # ── Dashboard Stats ───────────────────────────────────────────────

    async def increment_counter(self, key: str, ttl: int = 86400):
        count = await self.client.incr(f"counter:{key}")
        await self.client.expire(f"counter:{key}", ttl)
        return count

    async def get_counter(self, key: str) -> int:
        val = await self.client.get(f"counter:{key}")
        return int(val) if val else 0


def get_redis() -> RedisService:
    global _instance
    if _instance is None:
        _instance = RedisService()
    return _instance
