# src/schemas/models.py
from pydantic import BaseModel, Field

class TransactionEvent(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    user_id: str = Field(..., description="User unique identifier")
    amount: float = Field(..., gt=0, description="Transaction amount in currency units")
    device_id: str = Field(..., description="Device fingerprint ID")
    ip_address: str = Field(..., description="Originating IP address")

class ScoringResponse(BaseModel):
    transaction_id: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    is_anomaly: bool
    collusive_ring_detected: bool
    latency_ms: float