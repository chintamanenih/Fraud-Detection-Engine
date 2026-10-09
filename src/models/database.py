# src/models/database.py
from sqlalchemy import create_engine, Column, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./fraud_engine.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TransactionRecord(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    amount = Column(Float)
    device_id = Column(String, index=True)
    ip_address = Column(String)
    risk_score = Column(Float)
    is_anomaly = Column(Boolean)
    collusive_ring_detected = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

# Automatically create tables on module import so tests and app have them ready
init_db()