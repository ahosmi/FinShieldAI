"""
FinShield AI — Train Isolation Forest on synthetic transaction data.
Run once before starting fraud-detection service.
"""

import json
import random
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "isolation_forest.pkl")
N_NORMAL = 10000
N_FRAUD = 700   # ~7% fraud rate


def generate_training_data():
    records = []

    # Normal transactions
    for _ in range(N_NORMAL):
        hour = random.choices(range(24), weights=[1,1,1,1,1,2,5,8,10,10,10,10,10,10,10,10,10,10,10,10,10,10,8,4])[0]
        records.append({
            "amount":              max(10, round(random.lognormvariate(7.0, 1.2), 2)),
            "hour_of_day":         hour,
            "day_of_week":         random.randint(0, 6),
            "txn_count_5m":        random.randint(1, 4),
            "total_amount_5m":     random.uniform(100, 10000),
            "unique_devices_5m":   1,
            "unique_merchants_5m": random.randint(1, 3),
            "avg_amount_5m":       random.uniform(100, 5000),
            "label": 0,
        })

    # Fraud transactions — each pattern adds features that Isolation Forest will learn
    fraud_patterns = [
        # Velocity abuse: many txns, small amounts
        lambda: {"amount": random.uniform(50, 499), "hour_of_day": random.randint(0,23),
                 "day_of_week": random.randint(0,6), "txn_count_5m": random.randint(16,50),
                 "total_amount_5m": random.uniform(5000,30000), "unique_devices_5m": 1,
                 "unique_merchants_5m": random.randint(1,3), "avg_amount_5m": random.uniform(50,499), "label": 1},
        # Device switching
        lambda: {"amount": random.uniform(5000,50000), "hour_of_day": random.randint(0,23),
                 "day_of_week": random.randint(0,6), "txn_count_5m": random.randint(3,8),
                 "total_amount_5m": random.uniform(20000,150000), "unique_devices_5m": random.randint(3,7),
                 "unique_merchants_5m": random.randint(1,5), "avg_amount_5m": random.uniform(5000,50000), "label": 1},
        # Night anomaly: high amount + night hours
        lambda: {"amount": random.uniform(50000,500000), "hour_of_day": random.choice([2,3,4]),
                 "day_of_week": random.randint(0,6), "txn_count_5m": random.randint(1,3),
                 "total_amount_5m": random.uniform(50000,500000), "unique_devices_5m": 1,
                 "unique_merchants_5m": 1, "avg_amount_5m": random.uniform(50000,500000), "label": 1},
        # Mule account: structured amounts
        lambda: {"amount": random.uniform(9000,9999), "hour_of_day": random.randint(0,23),
                 "day_of_week": random.randint(0,6), "txn_count_5m": random.randint(5,15),
                 "total_amount_5m": random.uniform(45000,90000), "unique_devices_5m": 1,
                 "unique_merchants_5m": random.randint(1,3), "avg_amount_5m": random.uniform(9000,9999), "label": 1},
    ]

    for _ in range(N_FRAUD):
        pattern = random.choice(fraud_patterns)
        records.append(pattern())

    df = pd.DataFrame(records)
    return df


FEATURES = [
    "amount", "hour_of_day", "day_of_week",
    "txn_count_5m", "total_amount_5m",
    "unique_devices_5m", "unique_merchants_5m", "avg_amount_5m",
]


def train():
    print("Generating training data...")
    df = generate_training_data()
    X = df[FEATURES].fillna(0)

    print(f"Training Isolation Forest on {len(X)} samples ({N_NORMAL} normal + {N_FRAUD} fraud)...")
    model = IsolationForest(
        n_estimators=200,
        contamination=0.065,
        max_features=len(FEATURES),
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)

    # Quick validation
    preds = model.predict(X)
    predicted_fraud = (preds == -1).sum()
    print(f"Model predicts {predicted_fraud} anomalies ({predicted_fraud/len(X)*100:.1f}%)")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    joblib.dump(model, OUTPUT_PATH)
    print(f"Model saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    train()
