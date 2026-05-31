"""
Simulates high-volume UPI/wallet/merchant payment streams with fraud scenarios.
"""

import asyncio
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

from kafka import KafkaProducer
from fraud_scenarios import FraudScenarioEngine
from event_schemas import Transaction

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TPS = int(os.getenv("TRANSACTIONS_PER_SECOND", "50"))
FRAUD_RATE = float(os.getenv("FRAUD_RATE", "0.07"))

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks="all",
    retries=3,
    linger_ms=5,
    batch_size=16384,
)

TRANSACTION_TYPES = ["UPI", "WALLET", "MERCHANT", "REFUND", "NETBANKING"]
STATUS_WEIGHTS = {"SUCCESS": 0.85, "FAILED": 0.10, "PENDING": 0.05}
BANKS = ["HDFC", "ICICI", "SBI", "AXIS", "KOTAK", "YES", "INDUSIND"]
APPS = ["PhonePe", "GPay", "Paytm", "BHIM", "AmazonPay"]
CITIES = [
    {"city": "Mumbai",    "lat": 19.0760, "lon": 72.8777, "region": "MH"},
    {"city": "Delhi",     "lat": 28.6139, "lon": 77.2090, "region": "DL"},
    {"city": "Bangalore", "lat": 12.9716, "lon": 77.5946, "region": "KA"},
    {"city": "Chennai",   "lat": 13.0827, "lon": 80.2707, "region": "TN"},
    {"city": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "region": "TS"},
    {"city": "Pune",      "lat": 18.5204, "lon": 73.8567, "region": "MH"},
    {"city": "Kolkata",   "lat": 22.5726, "lon": 88.3639, "region": "WB"},
    {"city": "Ahmedabad", "lat": 23.0225, "lon": 72.5714, "region": "GJ"},
]

fraud_engine = FraudScenarioEngine()


def generate_normal_transaction(user_id: str, device_id: str, location: dict) -> dict:
    txn_type = random.choice(TRANSACTION_TYPES)
    amount = round(random.lognormvariate(7.0, 1.5), 2)
    amount = max(10.0, min(amount, 500000.0))

    return {
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "merchant_id": f"mrc_{random.randint(1000, 9999)}",
        "amount": amount,
        "currency": "INR",
        "transaction_type": txn_type,
        "status": random.choices(
            list(STATUS_WEIGHTS.keys()), weights=list(STATUS_WEIGHTS.values())
        )[0],
        "device_id": device_id,
        "ip_address": f"103.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
        "geo_lat": round(location["lat"] + random.uniform(-0.05, 0.05), 6),
        "geo_lon": round(location["lon"] + random.uniform(-0.05, 0.05), 6),
        "region": location["region"],
        "city": location["city"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "bank": random.choice(BANKS),
            "app": random.choice(APPS),
            "upi_handle": f"user{random.randint(1000,9999)}@okaxis",
        },
        "is_synthetic_fraud": False,
        "fraud_scenario": None,
    }


async def run_generator(tps: int = TPS, fraud_rate: float = FRAUD_RATE):
    num_users = 500
    users = [f"usr_{uuid.uuid4().hex[:8]}" for _ in range(num_users)]
    devices = {u: f"dev_{uuid.uuid4().hex[:8]}" for u in users}
    locations = {u: random.choice(CITIES) for u in users}

    total_sent = 0
    fraud_sent = 0
    start_time = time.time()

    print(f"[Generator] Starting: {tps} TPS | Fraud rate: {fraud_rate*100:.0f}%")
    print(f"[Generator] Pool: {num_users} synthetic users | Kafka: {KAFKA_BOOTSTRAP_SERVERS}")

    while True:
        batch_start = time.monotonic()

        for _ in range(tps):
            user = random.choice(users)

            if random.random() < fraud_rate:
                event = fraud_engine.generate_fraud_event(user, devices[user], locations[user])
                fraud_sent += 1
            else:
                event = generate_normal_transaction(user, devices[user], locations[user])

            producer.send("transactions", value=event, key=user.encode())
            total_sent += 1

        producer.flush()
        elapsed = time.monotonic() - batch_start

        
        if total_sent % (tps * 10) == 0:
            uptime = time.time() - start_time
            actual_tps = total_sent / uptime
            print(
                f"[Generator] Sent: {total_sent:,} | Fraud: {fraud_sent:,} "
                f"({fraud_sent/total_sent*100:.1f}%) | Actual TPS: {actual_tps:.0f}"
            )

        await asyncio.sleep(max(0, 1.0 - elapsed))


if __name__ == "__main__":
    asyncio.run(run_generator())
