# 🤖 PredictAI — Agentic Predictive Maintenance Agent
**Team: beyondminus | Hackathon: Hack Malenadu**  
Mallikarjun Paroji · Jeet Mundra · Vraj Joisar · Sumanth KS

---

## 🏗 Project Structure

```
predictive-maintenance-agent/
├── producer/               # Kafka sensor simulator (4 machines)
├── consumer/               # Kafka consumer → ML pipeline
├── features/               # Feature engineering (rolling, lag, z-score)
├── models/                 # Isolation Forest, XGBoost, Z-score, LSTM
├── fusion/                 # Hybrid Risk Score engine (weighted fusion)
├── agent/                  # Decision engine + explainer (agentic actions)
├── alerts/                 # Twilio SMS + ElevenLabs Voice Call
├── maintenance/            # Maintenance auto-scheduler
├── api/                    # FastAPI backend (SSE streaming)
├── database/               # PostgreSQL schema + SQLAlchemy models
├── celery_app.py           # Async task queue (Redis + Celery)
├── dashboard/              # Next.js frontend (live readings, alerts)
├── docker-compose.yml      # Infrastructure (Kafka, Redis, Postgres)
├── requirements.txt        # Python dependencies
└── .env.example            # Environment config template
```

---

## 🚀 Quick Start

### 1. Infrastructure
```bash
docker-compose up -d
```

### 2. Python Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Configure API keys
```bash
cp .env.example .env        # Then edit .env with your Twilio / ElevenLabs keys
```

### 4. Start the Backend
```bash
# Terminal 1 — Sensor Simulator
python producer/sensor_simulator.py

# Terminal 2 — Kafka Consumer (ML Pipeline starts here)
python consumer/kafka_consumer.py

# Terminal 3 — FastAPI
uvicorn api.main:app --reload --port 8000

# Terminal 4 — Celery Worker
celery -A celery_app worker --loglevel=info
```

### 5. Start the Dashboard
```bash
cd dashboard
npm run dev
```
Open: http://localhost:3000

---

## 🧠 How the AI Works

| Layer | What it does |
|---|---|
| **Kafka** | Ingests 4 machine streams at 1 reading/sec |
| **Feature Engine** | Computes rolling stats, lag values, Z-scores, trend slopes |
| **Isolation Forest** | Detects unseen/unknown anomaly patterns |
| **XGBoost** | Detects compound multi-sensor failures |
| **Z-Score Engine** | Fast rule-based spike detection |
| **LSTM Autoencoder** | Temporal drift / gradual degradation |
| **Risk Fusion Engine** | `Risk = 0.4*RF + 0.3*ISO + 0.2*Z + 0.1*LSTM` |
| **Agent Decision Engine** | `LOW→log · MEDIUM→dashboard · HIGH→SMS · CRITICAL→voice call` |
| **Explainer** | Generates human-readable reason for every alert |

---

## 🔥 Hackathon Demo Flow

1. `docker-compose up -d`
2. Start all 4 terminals above
3. Open dashboard at `http://localhost:3000`
4. All machines show **HEALTHY** (green)
5. Click **"⚡ Inject Anomaly"** on Machine M2
6. Watch the risk score climb: `0.12 → 0.54 → 0.87`
7. Dashboard card turns **RED**
8. Alert appears with plain-English explanation
9. SMS sent to engineer's phone (if Twilio keys set)
10. Voice call triggered with ElevenLabs synthesized speech

---

## 📦 Tech Stack

| Component | Technology |
|---|---|
| Streaming | Apache Kafka |
| Backend | FastAPI + Python |
| ML Models | scikit-learn, XGBoost |
| Deep Learning | TensorFlow/Keras (LSTM) |
| Async Queue | Redis + Celery |
| Storage | PostgreSQL |
| Frontend | Next.js + Recharts |
| SMS | Twilio |
| Voice | Twilio + ElevenLabs |
| Containerisation | Docker Compose |

---

> **Note:** The dashboard works in **Simulation Mode** even without the backend running — it generates realistic sensor data locally for demo purposes.
