# Real-Time Fraud & Anomaly Detection Engine

A production-grade, high-performance fraud detection backend service combining **Isolation Forest** (unsupervised anomaly detection) and **NetworkX** (graph-based collusion ring analysis). Built with **FastAPI**, **Pydantic**, and a clean modular architecture.

---

## 🏗️ Architecture & Project Structure

The project follows a strict enterprise `src/` layout pattern to ensure clean separation of concerns, robust path resolution, and seamless testability:

```text
fraud-detection-engine/
├── Dockerfile
├── docker-compose.yml
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── app.py            # FastAPI entrypoint and routing
│   ├── models/
│   │   ├── __init__.py
│   │   └── fraud_engine.py   # Core ML & Graph analytics engine
│   └── schemas/
│       ├── __init__.py
│       └── models.py         # Pydantic validation models
└── tests/
    └── test_api.py           # Pytest integration suite


🚀 Getting Started
1. Installation
Clone the repository and install the required dependencies:

PowerShell
pip install -r requirements.txt
2. Running the API Server
Launch the application locally using Uvicorn with hot-reloading enabled:

PowerShell
python -m uvicorn src.api.app:app --reload
The server will spin up at http://127.0.0.1:8000. You can access the interactive Swagger documentation directly at http://127.0.0.1:8000/docs.

🧪 Running Tests
Verify the integrity of the application using pytest:

PowerShell
python -m pytest
📡 API Endpoints
GET / - Root status check.

GET /health - System health and engine status.

POST /v1/score - Evaluates a transaction payload and returns risk metrics, anomaly tags, and graph collusion flags.

Example Scoring Request Payload
JSON
{
  "transaction_id": "tx_101",
  "user_id": "user_99",
  "amount": 250.50,
  "device_id": "device_abc",
  "ip_address": "192.168.1.15"
}