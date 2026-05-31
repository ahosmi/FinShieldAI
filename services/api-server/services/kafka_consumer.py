"""FinShield AI — Kafka Consumer Service (API Server side)"""

import json
import logging
import os
from aiokafka import AIOKafkaConsumer

logger = logging.getLogger("kafka-consumer")
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


class FraudAlertConsumer:
    def __init__(self, redis_svc, pg_svc, ws_manager):
        self.redis  = redis_svc
        self.pg     = pg_svc
        self.ws     = ws_manager

    async def start(self):
        consumer = AIOKafkaConsumer(
            "fraud-alerts",
            bootstrap_servers=KAFKA_SERVERS,
            group_id="api-server-relay",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="latest",
        )
        await consumer.start()
        logger.info("API Kafka consumer started (topic: fraud-alerts)")
        try:
            async for msg in consumer:
                await self._handle(msg.value)
        finally:
            await consumer.stop()

    async def _handle(self, alert: dict):
        txn_id = alert.get("transaction_id", "")
        # Cache in Redis
        await self.redis.set_alert(txn_id, alert)
        if alert.get("risk_score", 0) >= 80:
            await self.redis.add_to_active_suspicious(
                alert.get("user_id", ""), alert.get("risk_score", 0)
            )
        # Persist to PostgreSQL
        await self.pg.insert_fraud_decision(alert)
        # Push to WebSocket clients
        await self.ws.broadcast({"type": "FRAUD_ALERT", "payload": alert})
        logger.debug(f"Relayed alert {txn_id} to {self.ws.count} WS clients")
