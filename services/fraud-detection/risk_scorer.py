"""
FinShield AI — Composite Risk Scorer
Combines rule-based + ML + historical risk into a single 0-100 score.
"""

import logging
from typing import List
from .rule_engine import FraudRuleEngine, RuleTrigger
from .ml_detector import FraudMLDetector

logger = logging.getLogger(__name__)


class CompositeRiskScorer:
    RULE_WEIGHT = 0.45
    ML_WEIGHT = 0.35
    HISTORICAL_WEIGHT = 0.20

    DECISIONS = [
        ("BLOCK",     80, 100),
        ("CHALLENGE", 60,  80),
        ("MONITOR",   30,  60),
        ("ALLOW",      0,  30),
    ]

    def __init__(self, rule_engine: FraudRuleEngine, ml_detector: FraudMLDetector):
        self.rules = rule_engine
        self.ml = ml_detector

    def score(self, txn: dict, velocity: dict, historical_risk: float = 0.0) -> dict:
        rule_score, triggers = self.rules.evaluate(txn, velocity)
        ml_score_raw = self.ml.predict_score(txn, velocity)
        ml_score = ml_score_raw * 100

        composite = (
            rule_score       * self.RULE_WEIGHT +
            ml_score         * self.ML_WEIGHT +
            historical_risk  * self.HISTORICAL_WEIGHT
        )
        composite = round(min(composite, 100.0), 2)
        decision = self._get_decision(composite)

        return {
            "transaction_id": txn["transaction_id"],
            "user_id": txn["user_id"],
            "merchant_id": txn.get("merchant_id"),
            "amount": txn.get("amount"),
            "region": txn.get("region"),
            "city": txn.get("city"),
            "transaction_type": txn.get("transaction_type"),
            "risk_score": composite,
            "rule_score": round(rule_score, 2),
            "ml_score": round(ml_score, 2),
            "historical_risk": round(historical_risk, 2),
            "decision": decision,
            "rule_triggers": [vars(t) for t in triggers],
            "fraud_type": triggers[0].rule_id if triggers else None,
            "fraud_scenario": txn.get("fraud_scenario"),
            "is_fraud": composite >= 60,
            "timestamp": txn.get("timestamp"),
        }

    def _get_decision(self, score: float) -> str:
        for decision, low, high in self.DECISIONS:
            if low <= score < high:
                return decision
        return "BLOCK"
