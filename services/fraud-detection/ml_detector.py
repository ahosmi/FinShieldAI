"""
FinShield AI — ML-Based Fraud Detector
Uses Isolation Forest for multi-dimensional anomaly detection.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

FEATURES = [
    "amount",
    "hour_of_day",
    "day_of_week",
    "txn_count_5m",
    "total_amount_5m",
    "unique_devices_5m",
    "unique_merchants_5m",
    "avg_amount_5m",
]


class FraudMLDetector:
    def __init__(self, model_path: str = "models/isolation_forest.pkl"):
        self.model = None
        self.model_path = model_path
        self._load()

    def _load(self):
        try:
            import joblib
            self.model = joblib.load(self.model_path)
            logger.info(f"ML model loaded from {self.model_path}")
        except FileNotFoundError:
            logger.warning(f"No model at {self.model_path} — ML scoring disabled. Run train_model.py first.")

    def predict_score(self, txn: dict, velocity: dict) -> float:
        """Returns 0.0 (normal) to 1.0 (highly anomalous)."""
        if self.model is None:
            return 0.0
        try:
            from datetime import datetime
            ts = txn.get("timestamp", "")
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            features = {
                "amount": txn.get("amount", 0),
                "hour_of_day": dt.hour,
                "day_of_week": dt.weekday(),
                "txn_count_5m": velocity.get("txn_count_5m", 1),
                "total_amount_5m": velocity.get("total_amount_5m", txn.get("amount", 0)),
                "unique_devices_5m": velocity.get("unique_devices_5m", 1),
                "unique_merchants_5m": velocity.get("unique_merchants_5m", 1),
                "avg_amount_5m": velocity.get("avg_amount_5m", txn.get("amount", 0)),
            }
            X = np.array([[features.get(f, 0) for f in FEATURES]])
            raw_score = self.model.decision_function(X)[0]
            # Convert: more negative = more anomalous → higher fraud probability
            normalized = float(1 / (1 + np.exp(raw_score * 3)))
            return round(normalized, 4)
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return 0.0
