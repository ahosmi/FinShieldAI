"""FinShield AI — Event Schema Definitions"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Transaction:
    transaction_id: str
    user_id: str
    merchant_id: str
    amount: float
    currency: str
    transaction_type: str
    status: str
    device_id: str
    ip_address: str
    geo_lat: float
    geo_lon: float
    region: str
    city: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_synthetic_fraud: bool = False
    fraud_scenario: Optional[str] = None
