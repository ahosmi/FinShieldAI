"""FinShield AI — PostgreSQL Service"""

import json
import logging
import os
from typing import List, Optional

import asyncpg

logger = logging.getLogger("postgres-service")
PG_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql+asyncpg://finshield:finshield_secure_pass@localhost:5432/finshield",
)

_instance: Optional["PostgresService"] = None


def _pg_dsn(url: str) -> str:
    """Convert SQLAlchemy-style URL to asyncpg DSN."""
    return url.replace("postgresql+asyncpg://", "postgresql://")


class PostgresService:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(_pg_dsn(PG_URL), min_size=2, max_size=10)
        logger.info("PostgreSQL pool created")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    # ── Write ─────────────────────────────────────────────────────────

    async def insert_fraud_decision(self, alert: dict):
        sql = """
            INSERT INTO fraud_decisions
                (transaction_id, user_id, amount, risk_score, fraud_type,
                 decision, rule_triggers, ml_score, fraud_scenario, timestamp)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
            ON CONFLICT (transaction_id) DO NOTHING
        """
        await self.pool.execute(
            sql,
            alert.get("transaction_id"),
            alert.get("user_id"),
            alert.get("amount"),
            alert.get("risk_score"),
            alert.get("fraud_type"),
            alert.get("decision"),
            json.dumps(alert.get("rule_triggers", [])),
            alert.get("ml_score"),
            alert.get("fraud_scenario"),
            alert.get("timestamp"),
        )

    # ── Read ──────────────────────────────────────────────────────────

    async def fetch_recent_alerts(self, limit: int = 20) -> List[dict]:
        rows = await self.pool.fetch(
            "SELECT * FROM fraud_decisions ORDER BY created_at DESC LIMIT $1", limit
        )
        return [dict(r) for r in rows]

    async def fetch_alert_by_txn(self, txn_id: str) -> Optional[dict]:
        row = await self.pool.fetchrow(
            "SELECT * FROM fraud_decisions WHERE transaction_id = $1", txn_id
        )
        return dict(row) if row else None

    async def fetch_transactions(self, limit: int, offset: int) -> List[dict]:
        rows = await self.pool.fetch(
            "SELECT * FROM fraud_decisions ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            limit, offset,
        )
        return [dict(r) for r in rows]

    async def fetch_transaction(self, txn_id: str) -> Optional[dict]:
        row = await self.pool.fetchrow(
            "SELECT * FROM fraud_decisions WHERE transaction_id = $1", txn_id
        )
        return dict(row) if row else None

    async def fetch_dashboard_stats(self) -> dict:
        row = await self.pool.fetchrow("""
            SELECT
                COUNT(*)                                            AS total,
                COUNT(*) FILTER (WHERE decision IN ('BLOCK','CHALLENGE')) AS fraud_count,
                COALESCE(SUM(amount) FILTER (WHERE decision = 'BLOCK'), 0) AS blocked_amount,
                ROUND(AVG(risk_score)::numeric, 2)                 AS avg_risk
            FROM fraud_decisions
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """)
        d = dict(row)
        total = d["total"] or 1
        d["fraud_rate"] = round(float(d["fraud_count"]) / total * 100, 2)
        return d

    async def fetch_risk_distribution(self) -> dict:
        rows = await self.pool.fetch("""
            SELECT decision, COUNT(*) AS count
            FROM fraud_decisions
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY decision
        """)
        return {r["decision"]: r["count"] for r in rows}

    async def fetch_fraud_by_type(self) -> List[dict]:
        rows = await self.pool.fetch("""
            SELECT fraud_scenario, COUNT(*) AS count
            FROM fraud_decisions
            WHERE fraud_scenario IS NOT NULL
              AND created_at > NOW() - INTERVAL '24 hours'
            GROUP BY fraud_scenario
            ORDER BY count DESC
        """)
        return [dict(r) for r in rows]

    async def fetch_merchant_risk_summary(self, limit: int) -> List[dict]:
        rows = await self.pool.fetch("""
            SELECT
                merchant_id,
                COUNT(*)                                                AS total_txns,
                COUNT(*) FILTER (WHERE decision IN ('BLOCK','CHALLENGE')) AS fraud_txns,
                ROUND(AVG(risk_score)::numeric, 2)                      AS avg_risk,
                COALESCE(SUM(amount) FILTER (WHERE decision = 'BLOCK'), 0) AS blocked_amount
            FROM fraud_decisions
            GROUP BY merchant_id
            ORDER BY avg_risk DESC
            LIMIT $1
        """, limit)
        return [dict(r) for r in rows]

    async def fetch_merchant(self, merchant_id: str) -> Optional[dict]:
        row = await self.pool.fetchrow(
            "SELECT * FROM merchants WHERE merchant_id = $1", merchant_id
        )
        return dict(row) if row else None


def get_postgres() -> PostgresService:
    global _instance
    if _instance is None:
        _instance = PostgresService()
    return _instance
