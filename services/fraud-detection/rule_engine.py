"""
FinShield AI — Rule-Based Fraud Detection Engine
Deterministic, zero-ML rules that fire in < 1ms.
"""

import json
import logging
from dataclasses import dataclass, asdict
from typing import List, Tuple
from datetime import datetime, timezone

import redis as redis_lib

logger = logging.getLogger(__name__)


@dataclass
class RuleTrigger:
    rule_id: str
    description: str
    score_contribution: int
    severity: str  


class FraudRuleEngine:

    def __init__(self, redis_client: redis_lib.Redis):
        self.redis = redis_client

    def evaluate(
        self, txn: dict, velocity: dict
    ) -> Tuple[float, List[RuleTrigger]]:
        """
        Evaluate all rules against a transaction and its velocity metrics.
        Returns (rule_score 0-100, list_of_triggered_rules).
        """
        triggers: List[RuleTrigger] = []
        score = 0

        def add(rule: RuleTrigger):
            triggers.append(rule)
            nonlocal score
            score += rule.score_contribution

        # ── R001: Transaction Velocity ────────────────────────────────
        txn_count = velocity.get("txn_count_5m", 0)
        if txn_count > 20:
            add(RuleTrigger("R001", f"Critical velocity: {txn_count} txns in 5 min", 50, "CRITICAL"))
        elif txn_count > 10:
            add(RuleTrigger("R001", f"High velocity: {txn_count} txns in 5 min", 30, "HIGH"))

        # ── R002: Device Switching ────────────────────────────────────
        unique_devices = velocity.get("unique_devices_5m", 1)
        if unique_devices >= 4:
            add(RuleTrigger("R002", f"Severe device switching: {unique_devices} devices in 5 min", 45, "CRITICAL"))
        elif unique_devices >= 2:
            add(RuleTrigger("R002", f"Device switching: {unique_devices} devices in 5 min", 25, "HIGH"))

        # ── R003: Night-Time Large Transaction ────────────────────────
        try:
            ts = txn.get("timestamp", "")
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            hour = dt.hour
        except Exception:
            hour = 12

        if hour in [1, 2, 3, 4] and txn.get("amount", 0) > 50000:
            add(RuleTrigger(
                "R003",
                f"Night anomaly: ₹{txn['amount']:,.0f} at {hour:02d}:00 hrs",
                25, "MEDIUM"
            ))

        # ── R004: Bot Activity Signature ──────────────────────────────
        amount = txn.get("amount", 0)
        geo_lat = txn.get("geo_lat", 1)
        geo_lon = txn.get("geo_lon", 1)
        ip = txn.get("ip_address", "")
        if amount == int(amount) and geo_lat == 0.0 and geo_lon == 0.0:
            add(RuleTrigger("R004", "Bot signature: round amount + zero geolocation", 50, "CRITICAL"))
        elif ip.startswith("10.") or ip.startswith("192.168."):
            add(RuleTrigger("R004", f"Suspicious internal/spoofed IP: {ip}", 20, "MEDIUM"))

        # ── R005: International / Unknown Region ──────────────────────
        if txn.get("region") == "INTERNATIONAL":
            add(RuleTrigger("R005", f"Transaction from international location: {txn.get('city')}", 30, "MEDIUM"))
        elif txn.get("region") == "UNKNOWN":
            add(RuleTrigger("R005", "Unknown region/geolocation", 25, "MEDIUM"))

        # ── R006: Known Fraud Scenario Tag ────────────────────────────
        fraud_scenario = txn.get("fraud_scenario")
        if fraud_scenario:
            scenario_scores = {
                "VELOCITY_ABUSE":   40,
                "DEVICE_SWITCHING": 35,
                "GEO_IMPOSSIBLE":   50,
                "REFUND_CYCLING":   30,
                "BOT_ACTIVITY":     50,
                "NIGHT_ANOMALY":    25,
                "MULE_ACCOUNT":     40,
            }
            s = scenario_scores.get(fraud_scenario, 20)
            add(RuleTrigger("R006", f"Synthetic fraud scenario: {fraud_scenario}", s, "CRITICAL"))

        # ── R007: Refund Frequency ────────────────────────────────────
        if txn.get("transaction_type") == "REFUND":
            refund_key = f"refund_count:{txn['user_id']}"
            try:
                refund_count = int(self.redis.get(refund_key) or 0)
                if refund_count > 5:
                    add(RuleTrigger("R007", f"Refund abuse: {refund_count} refunds in 1 hr", 35, "HIGH"))
                pipe = self.redis.pipeline()
                pipe.incr(refund_key)
                pipe.expire(refund_key, 3600)
                pipe.execute()
            except Exception as e:
                logger.warning(f"Redis refund counter error: {e}")

        # ── R008: Amount Structuring (just below thresholds) ──────────
        if 9000 <= amount <= 9999:
            add(RuleTrigger("R008", f"Possible structuring: ₹{amount:,.0f} (below ₹10K threshold)", 20, "MEDIUM"))
        elif 49000 <= amount <= 49999:
            add(RuleTrigger("R008", f"Possible structuring: ₹{amount:,.0f} (below ₹50K threshold)", 15, "LOW"))

        # ── R009: High Amount Single Transaction ──────────────────────
        if amount > 100000:
            add(RuleTrigger("R009", f"High-value transaction: ₹{amount:,.0f}", 15, "LOW"))

        # ── R010: Many Unique Merchants ───────────────────────────────
        unique_merchants = velocity.get("unique_merchants_5m", 0)
        if unique_merchants > 8:
            add(RuleTrigger("R010", f"Merchant hopping: {unique_merchants} merchants in 5 min", 20, "MEDIUM"))

        return min(score, 100), triggers
