"""
Generates realistic synthetic fraud events for 7 major fraud patterns.
"""

import random
import uuid
from datetime import datetime, timezone


class FraudScenarioEngine:

    SCENARIO_WEIGHTS = [
        ("velocity_abuse",   0.20),
        ("device_switching", 0.15),
        ("geo_impossible",   0.15),
        ("refund_cycling",   0.15),
        ("bot_activity",     0.15),
        ("night_anomaly",    0.10),
        ("mule_account",     0.10),
    ]

    def generate_fraud_event(self, user_id: str, device_id: str, location: dict) -> dict:
        scenarios, weights = zip(*self.SCENARIO_WEIGHTS)
        scenario_name = random.choices(scenarios, weights=weights)[0]
        method = getattr(self, f"_{scenario_name}")
        return method(user_id, device_id, location)

    # ── Scenario 1: Velocity Abuse ────────────────────────────────────
    def _velocity_abuse(self, user_id, device_id, location):
        return {
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "merchant_id": f"mrc_{random.randint(1000, 1010)}",  
            "amount": round(random.uniform(50, 499), 2),          
            "currency": "INR",
            "transaction_type": "UPI",
            "status": "SUCCESS",
            "device_id": device_id,
            "ip_address": "103.24.91.12",
            "geo_lat": location["lat"],
            "geo_lon": location["lon"],
            "region": location["region"],
            "city": location["city"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {"bank": "HDFC", "app": "PhonePe", "upi_handle": f"fraud{random.randint(1,999)}@okaxis"},
            "is_synthetic_fraud": True,
            "fraud_scenario": "VELOCITY_ABUSE",
        }

    # ── Scenario 2: Device Switching ──────────────────────────────────
    def _device_switching(self, user_id, device_id, location):
        return {
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "merchant_id": f"mrc_{random.randint(1000, 9999)}",
            "amount": round(random.uniform(5000, 50000), 2),
            "currency": "INR",
            "transaction_type": "WALLET",
            "status": "SUCCESS",
            "device_id": f"dev_{uuid.uuid4().hex[:8]}",            
            "ip_address": f"45.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
            "geo_lat": location["lat"],
            "geo_lon": location["lon"],
            "region": location["region"],
            "city": location["city"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {"bank": "ICICI", "app": "GPay", "upi_handle": f"user{random.randint(1,999)}@oksbi"},
            "is_synthetic_fraud": True,
            "fraud_scenario": "DEVICE_SWITCHING",
        }

    # ── Scenario 3: Geo-Impossible ────────────────────────────────────
    def _geo_impossible(self, user_id, device_id, location):
        impossible_locations = [
            {"lat": 51.5074,  "lon": -0.1278,   "city": "London",   "region": "INTERNATIONAL"},
            {"lat": 40.7128,  "lon": -74.0060,  "city": "New York",  "region": "INTERNATIONAL"},
            {"lat": 35.6762,  "lon": 139.6503,  "city": "Tokyo",     "region": "INTERNATIONAL"},
            {"lat": 48.8566,  "lon": 2.3522,    "city": "Paris",     "region": "INTERNATIONAL"},
            {"lat": -33.8688, "lon": 151.2093,  "city": "Sydney",    "region": "INTERNATIONAL"},
        ]
        loc = random.choice(impossible_locations)
        return {
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "merchant_id": f"mrc_{random.randint(1000, 9999)}",
            "amount": round(random.uniform(10000, 200000), 2),
            "currency": "INR",
            "transaction_type": "NETBANKING",
            "status": "SUCCESS",
            "device_id": device_id,
            "ip_address": f"192.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
            "geo_lat": loc["lat"],
            "geo_lon": loc["lon"],
            "region": loc["region"],
            "city": loc["city"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {"bank": "SBI", "app": "BHIM", "upi_handle": f"intl{random.randint(1,999)}@okicici"},
            "is_synthetic_fraud": True,
            "fraud_scenario": "GEO_IMPOSSIBLE",
        }

    # ── Scenario 4: Refund Cycling ────────────────────────────────────
    def _refund_cycling(self, user_id, device_id, location):
        return {
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "merchant_id": f"mrc_{random.randint(5000, 5010)}",   
            "amount": round(random.uniform(1000, 10000), 2),
            "currency": "INR",
            "transaction_type": "REFUND",
            "status": "SUCCESS",
            "device_id": device_id,
            "ip_address": f"103.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
            "geo_lat": location["lat"],
            "geo_lon": location["lon"],
            "region": location["region"],
            "city": location["city"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {"bank": "AXIS", "app": "Paytm", "upi_handle": f"refund{random.randint(1,999)}@okhdfcbank"},
            "is_synthetic_fraud": True,
            "fraud_scenario": "REFUND_CYCLING",
        }

    # ── Scenario 5: Bot Activity ──────────────────────────────────────
    def _bot_activity(self, user_id, device_id, location):
        return {
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "merchant_id": "mrc_0001",                            
            "amount": float(random.choice([1, 5, 10, 100, 500])), 
            "currency": "INR",
            "transaction_type": "UPI",
            "status": "SUCCESS",
            "device_id": device_id,
            "ip_address": "10.0.0.1",                              
            "geo_lat": 0.0,                                        
            "geo_lon": 0.0,
            "region": "UNKNOWN",
            "city": "UNKNOWN",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {"bank": "HDFC", "app": "API", "upi_handle": "bot001@okaxis"},
            "is_synthetic_fraud": True,
            "fraud_scenario": "BOT_ACTIVITY",
        }

    # ── Scenario 6: Night Anomaly ─────────────────────────────────────
    def _night_anomaly(self, user_id, device_id, location):
        now = datetime.now(timezone.utc)
        night_time = now.replace(hour=random.choice([2, 3, 4]), minute=random.randint(0, 59))
        return {
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "merchant_id": f"mrc_{random.randint(1000, 9999)}",
            "amount": round(random.uniform(50000, 500000), 2),     # Very high value at night
            "currency": "INR",
            "transaction_type": "NETBANKING",
            "status": "SUCCESS",
            "device_id": device_id,
            "ip_address": f"103.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
            "geo_lat": location["lat"],
            "geo_lon": location["lon"],
            "region": location["region"],
            "city": location["city"],
            "timestamp": night_time.isoformat(),
            "metadata": {"bank": "HDFC", "app": "NetBanking", "upi_handle": None},
            "is_synthetic_fraud": True,
            "fraud_scenario": "NIGHT_ANOMALY",
        }

    # ── Scenario 7: Mule Account ──────────────────────────────────────
    def _mule_account(self, user_id, device_id, location):
        # ₹9,000–9,999 stays below the ₹10,000 reporting threshold
        amount = round(random.uniform(9000, 9999), 2)
        return {
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "merchant_id": f"mrc_{random.randint(1000, 9999)}",
            "amount": amount,
            "currency": "INR",
            "transaction_type": "WALLET",
            "status": "SUCCESS",
            "device_id": device_id,
            "ip_address": f"103.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
            "geo_lat": location["lat"],
            "geo_lon": location["lon"],
            "region": location["region"],
            "city": location["city"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {"bank": "SBI", "app": "Paytm", "upi_handle": f"mule{random.randint(1,999)}@oksbi"},
            "is_synthetic_fraud": True,
            "fraud_scenario": "MULE_ACCOUNT",
        }
