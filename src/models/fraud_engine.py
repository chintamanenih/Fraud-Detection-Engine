# src/models/fraud_engine.py
import numpy as np
from sklearn.ensemble import IsolationForest
import networkx as nx
from datetime import datetime, timezone, timedelta

class FraudEngine:
    def __init__(self):
        # Baseline training features: [amount, hour_of_day, velocity_count]
        X_train = np.array([
            [100.0, 14, 1],
            [250.0, 10, 1],
            [50.0, 18, 2],
            [1200.0, 22, 1],
            [45.0, 9, 1],
            [300.0, 15, 1],
            [500.0, 12, 1]
        ])
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(X_train)
        
        # Graph for syndicate / collusive ring detection
        self.graph = nx.Graph()
        self.graph.add_edge("user_1", "device_abc")
        self.graph.add_edge("user_2", "device_abc")  # Seed ring

    def analyze(self, tx, db_session=None):
        current_time = datetime.now(timezone.utc)
        hour_of_day = current_time.hour
        is_late_night = 0 <= hour_of_day <= 5  # Temporal pattern check[cite: 1, 2]

        user_amounts = []
        recent_velocity = 1

        # Query historical user profile from SQLite if available
        if db_session is not None:
            from src.models.database import TransactionRecord
            history = db_session.query(TransactionRecord).filter(TransactionRecord.user_id == tx.user_id).all()
            user_amounts = [h.amount for h in history]
            
            # Sliding-window velocity: transactions in the last 10 minutes[cite: 1, 2]
           # Sliding-window velocity: transactions in the last 10 minutes[cite: 1, 2]
        ten_mins_ago = current_time - timedelta(minutes=10)
        recent_velocity = 0
        for h in history:
            if h.timestamp:
                h_time = h.timestamp
                # If database timestamp is naive, make it timezone-aware (UTC)
                if h_time.tzinfo is None:
                    h_time = h_time.replace(tzinfo=timezone.utc)
                if h_time >= ten_mins_ago:
                    recent_velocity += 1
        recent_velocity = max(recent_velocity, 1)

        # Calculate User-Specific Z-Score for Amount
        if len(user_amounts) > 2:
            mean_amt = np.mean(user_amounts)
            std_amt = np.std(user_amounts) if np.std(user_amounts) > 0 else 1.0
            z_score = abs(tx.amount - mean_amt) / std_amt
        else:
            z_score = 0.0  # Default for new users without deep history

        # Isolation Forest baseline prediction
        features = np.array([[tx.amount, hour_of_day, recent_velocity]])
        pred = self.model.predict(features)[0]
        if_anomaly = True if pred == -1 else False
        if_score = 0.85 if if_anomaly else 0.20

        # Override anomaly flag if user Z-score deviates severely (> 3 standard deviations)[cite: 1, 2, 3]
        if z_score > 3.0:
            if_anomaly = True
            if_score = max(if_score, 0.90)

        # Graph Collusion Analysis
        self.graph.add_edge(tx.user_id, tx.device_id, relation="uses_device")
        self.graph.add_edge(tx.user_id, tx.ip_address, relation="connects_from_ip")

        collusive_ring = False
        for neighbor in self.graph.neighbors(tx.device_id):
            if neighbor != tx.user_id:
                collusive_ring = True
                break
        for neighbor in self.graph.neighbors(tx.ip_address):
            if neighbor != tx.user_id:
                collusive_ring = True
                break

        # Composite Risk Calculation
        base_risk = if_score
        if recent_velocity > 3:
            base_risk += 0.15
        if is_late_night:
            base_risk += 0.10
        if collusive_ring:
            base_risk = max(base_risk, 0.95)

        risk_score = min(max(base_risk, 0.0), 1.0)
        return risk_score, if_anomaly, collusive_ring

engine = FraudEngine()