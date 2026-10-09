# src/api/app.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import time
from sqlalchemy.orm import Session
from src.models.fraud_engine import engine as fraud_engine
from src.models.database import init_db, SessionLocal, TransactionRecord
from datetime import datetime, timezone
import traceback
import logging

app = FastAPI(
    title="Real-Time Fraud & Anomaly Detection Engine",
    version="1.0.0",
    description="Production-grade fraud detection API combining Isolation Forest and NetworkX graph analysis with SQLite persistence."
)

logger = logging.getLogger("SecurityAlerts")
logging.basicConfig(level=logging.INFO)

# Initialize SQLite database tables on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TransactionEvent(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    device_id: str
    ip_address: str

class ScoringResponse(BaseModel):
    transaction_id: str
    risk_score: float
    is_anomaly: bool
    collusive_ring_detected: bool
    latency_ms: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the Real-Time Fraud & Anomaly Detection Engine API"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "engine_loaded": True
    }

@app.post("/v1/score", response_model=ScoringResponse)
async def score_transaction(tx: TransactionEvent, db: Session = Depends(get_db)):
    t_start = time.perf_counter()
    try:
        # Pass DB session to evaluate user-specific historical baselines and velocity
        risk_score, is_anomaly, collusive_ring = fraud_engine.analyze(tx, db_session=db)
        latency_ms = (time.perf_counter() - t_start) * 1000.0
        
        if risk_score > 0.7 or collusive_ring or is_anomaly:
            alert_payload = {
                "severity": "CRITICAL" if collusive_ring or risk_score > 0.8 else "WARNING",
                "transaction_id": tx.transaction_id,
                "user_id": tx.user_id,
                "risk_score": round(risk_score, 4),
                "collusive_ring": collusive_ring,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            logger.warning(f"🚨 SECURITY ALERT DISPATCHED: {alert_payload}")

        db_record = TransactionRecord(
            transaction_id=tx.transaction_id,
            user_id=tx.user_id,
            amount=tx.amount,
            device_id=tx.device_id,
            ip_address=tx.ip_address,
            risk_score=round(risk_score, 4),
            is_anomaly=is_anomaly,
            collusive_ring_detected=collusive_ring
        )
        db.merge(db_record)
        db.commit()

        return ScoringResponse(
            transaction_id=tx.transaction_id,
            risk_score=round(risk_score, 4),
            is_anomaly=is_anomaly,
            collusive_ring_detected=collusive_ring,
            latency_ms=round(latency_ms, 2)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/transactions")
def get_transactions(db: Session = Depends(get_db)):
    records = db.query(TransactionRecord).order_by(TransactionRecord.timestamp.desc()).all()
    return records