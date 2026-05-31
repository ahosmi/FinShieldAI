import asyncio
import os
import asyncpg

PG_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql+asyncpg://finshield:finshield_secure_pass@localhost:5432/finshield",
).replace("postgresql+asyncpg://", "postgresql://")

DDL = """
-- Users
CREATE TABLE IF NOT EXISTS users (
    user_id     VARCHAR PRIMARY KEY,
    name        VARCHAR,
    email       VARCHAR,
    phone       VARCHAR,
    kyc_status  VARCHAR DEFAULT 'PENDING',
    risk_tier   VARCHAR DEFAULT 'LOW',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Merchants
CREATE TABLE IF NOT EXISTS merchants (
    merchant_id   VARCHAR PRIMARY KEY,
    name          VARCHAR,
    category      VARCHAR,
    risk_tier     VARCHAR DEFAULT 'LOW',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Core fraud decisions (one row per scored transaction)
CREATE TABLE IF NOT EXISTS fraud_decisions (
    id             SERIAL PRIMARY KEY,
    transaction_id VARCHAR UNIQUE NOT NULL,
    user_id        VARCHAR,
    merchant_id    VARCHAR,
    amount         NUMERIC(14,2),
    risk_score     NUMERIC(5,2),
    rule_score     NUMERIC(5,2),
    ml_score       NUMERIC(5,2),
    fraud_type     VARCHAR,
    fraud_scenario VARCHAR,
    decision       VARCHAR,         -- ALLOW | MONITOR | CHALLENGE | BLOCK
    rule_triggers  JSONB,
    rag_explanation TEXT,
    timestamp      TIMESTAMPTZ,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fd_user        ON fraud_decisions(user_id);
CREATE INDEX IF NOT EXISTS idx_fd_merchant    ON fraud_decisions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_fd_decision    ON fraud_decisions(decision);
CREATE INDEX IF NOT EXISTS idx_fd_created     ON fraud_decisions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_fd_risk_score  ON fraud_decisions(risk_score DESC);

-- Investigation cases
CREATE TABLE IF NOT EXISTS investigation_cases (
    case_id        SERIAL PRIMARY KEY,
    transaction_id VARCHAR REFERENCES fraud_decisions(transaction_id),
    investigator   VARCHAR,
    status         VARCHAR DEFAULT 'OPEN',   -- OPEN | IN_REVIEW | CLOSED | ESCALATED
    ai_summary     TEXT,
    notes          JSONB DEFAULT '[]',
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    updated_at     TIMESTAMPTZ DEFAULT NOW()
);
"""


async def init():
    conn = await asyncpg.connect(PG_URL)
    await conn.execute(DDL)
    await conn.close()
    print("PostgreSQL schema initialised successfully.")


if __name__ == "__main__":
    asyncio.run(init())
