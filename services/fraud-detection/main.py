"""
FinShield AI — Fraud Detection Service
Consumes enriched transactions from Kafka, scores them, publishes alerts.
"""

import asyncio
import json
import logging
import os

import redis.asyncio as aioredis
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from rule_engine import FraudRuleEngine
from ml_detector import FraudMLDetector
from risk_scorer import CompositeRiskScorer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("fraud-detection")

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
FRAUD_THRESHOLD = float(os.getenv("FRAUD_THRESHOLD", "60.0"))


async def main():
    # Init Redis
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

    # Build sync redis for rule engine (pipeline ops)
    import redis as sync_redis
    sync_r = sync_redis.from_url(REDIS_URL, decode_responses=True)

    # Init scorer
    rule_engine = FraudRuleEngine(sync_r)
    ml_detector = FraudMLDetector("models/isolation_forest.pkl")
    scorer = CompositeRiskScorer(rule_engine, ml_detector)

    # Kafka
    consumer = AIOKafkaConsumer(
        "transactions",
        bootstrap_servers=KAFKA_SERVERS,
        group_id="fraud-detection-group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",
    )

    await consumer.start()
    await producer.start()
    logger.info("Fraud Detection Service started. Consuming from 'transactions'...")

    processed = 0
    alerts = 0

    try:
        async for msg in consumer:
            txn = msg.value
            user_id = txn.get("user_id", "")

            # Fetch velocity metrics from Redis (set by Spark or simple counters)
            velocity = await _get_velocity(redis_client, user_id)

            # Get historical risk score
            historical_risk = float(await redis_client.get(f"historical_risk:{user_id}") or 20.0)

            # Score the transaction
            result = scorer.score(txn, velocity, historical_risk)

            # Update user risk in Redis
            await redis_client.setex(f"risk:{user_id}", 600, str(result["risk_score"]))

            # Publish to fraud-alerts topic if above threshold
            if result["risk_score"] >= FRAUD_THRESHOLD:
                await producer.send("fraud-alerts", value=result)
                await _cache_alert(redis_client, result)
                alerts += 1

                logger.info(
                    f"FRAUD ALERT | {result['transaction_id']} | "
                    f"Score: {result['risk_score']:.1f} | "
                    f"Decision: {result['decision']} | "
                    f"Type: {result.get('fraud_scenario', 'RULE_BASED')}"
                )

            processed += 1
            if processed % 500 == 0:
                logger.info(f"Processed: {processed:,} | Alerts: {alerts:,} | Rate: {alerts/processed*100:.1f}%")

    finally:
        await consumer.stop()
        await producer.stop()
        await redis_client.close()


async def _get_velocity(redis_client, user_id: str) -> dict:
    """Fetch pre-computed velocity metrics from Redis (set by Spark)."""
    try:
        raw = await redis_client.get(f"velocity:{user_id}")
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return {
        "txn_count_5m": 1,
        "total_amount_5m": 0,
        "unique_devices_5m": 1,
        "unique_merchants_5m": 1,
        "avg_amount_5m": 0,
    }


async def _cache_alert(redis_client, result: dict):
    """Cache fraud alert in Redis for dashboard relay."""
    txn_id = result["transaction_id"]
    pipe = redis_client.pipeline()
    pipe.setex(f"alert:{txn_id}", 3600, json.dumps(result))
    if result.get("risk_score", 0) >= 80:
        pipe.zadd("active_suspicious", {result["user_id"]: result["risk_score"]})
        pipe.expire("active_suspicious", 3600)
    await pipe.execute()


if __name__ == "__main__":
    asyncio.run(main())
