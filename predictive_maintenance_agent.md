# Predictive Maintenance Agent — Complete Build Guide
**Team: beyondminus | Hackathon: Hack Malenadu**  
**Members: Mallikarjun Paroji, Jeet Mundra, Vraj Joisar, Sumanth KS**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Proposed Solution](#3-proposed-solution)
4. [System Architecture — Layer by Layer](#4-system-architecture--layer-by-layer)
5. [Data Schema & Sensor Design](#5-data-schema--sensor-design)
6. [Layer 1: Data Ingestion (Kafka + FastAPI)](#6-layer-1-data-ingestion-kafka--fastapi)
7. [Layer 2: Baseline Learning Engine](#7-layer-2-baseline-learning-engine)
8. [Layer 3: Feature Engineering](#8-layer-3-feature-engineering)
9. [Layer 4: Hybrid Anomaly Detection Models](#9-layer-4-hybrid-anomaly-detection-models)
10. [Layer 5: Risk Score Fusion Engine](#10-layer-5-risk-score-fusion-engine)
11. [Layer 6: Agent Decision Engine](#11-layer-6-agent-decision-engine)
12. [Smart Alert & Escalation System](#12-smart-alert--escalation-system)
13. [Explainable AI (XAI) Layer](#13-explainable-ai-xai-layer)
14. [Backend API Structure (FastAPI)](#14-backend-api-structure-fastapi)
15. [Database Schema (PostgreSQL)](#15-database-schema-postgresql)
16. [Frontend Dashboard (Next.js)](#16-frontend-dashboard-nextjs)
17. [Async Jobs (Redis + Celery)](#17-async-jobs-redis--celery)
18. [Voice Alert System (Twilio + ElevenLabs)](#18-voice-alert-system-twilio--elevenlabs)
19. [Maintenance Scheduler](#19-maintenance-scheduler)
20. [Full Folder Structure](#20-full-folder-structure)
21. [Tech Stack Summary](#21-tech-stack-summary)
22. [End-to-End Demo Flow (Hackathon)](#22-end-to-end-demo-flow-hackathon)
23. [References](#23-references)

---

## 1. Project Overview

This project builds an **AI-powered Predictive Maintenance Agent** that:

- Connects to **live sensor streams** from 4 industrial machines via Kafka
- Uses **hybrid, multi-model anomaly detection** to catch failures early
- Computes a **unified risk score** and classifies severity
- **Automatically escalates** — dashboard → SMS → voice call → ticket
- Generates **human-readable explanations** for every alert
- Operates as a **fully autonomous agentic system**

Think of it as: *"Google Maps traffic prediction — but for industrial machines."*

---

## 2. Problem Statement

> Build an AI-powered Predictive Maintenance Agent that connects to live sensor streams from industrial machines, detects early warning patterns before failures occur, and generates intelligent alerts with clear, human-readable explanations. The system should support multi-machine monitoring and optionally automate maintenance scheduling.

**Core challenge:**  
Sensor data is **noisy** — not every anomaly indicates a failure. The agent must accurately distinguish real risk signals from transient noise and provide **trustworthy, explainable decisions**.

---

## 3. Proposed Solution

A Kafka-based streaming pipeline monitors 4 machines continuously with per-machine dynamic baselines. It uses a **hybrid multi-model approach**:

| Model | Purpose |
|---|---|
| XGBoost / Random Forest | Detect compound anomalies (multi-sensor combined) |
| Isolation Forest | Detect unknown/unseen behaviour |
| Statistical Engine (Z-score) | Detect spike violations above threshold |
| LSTM Autoencoder | Detect gradual temporal drift in sequences |

All model outputs are fused into a **single risk score** (0 to 1), which drives a severity decision (Low / Medium / High / Critical). An agent loop prioritises alerts across machines and triggers the correct escalation automatically.

---

## 4. System Architecture — Layer by Layer

```
/history API
   ↓
baseline training
   ↓
Isolation Forest
   ↓
XGBoost

/stream/{machine_id}
   ↓
Kafka(sensor_readings)
   ↓
Decision Engine
   ↓
POST /alert
   ↓
POST /schedule-maintenance
   ↓
Dashboard
```

---

## 5. Data Schema & Sensor Design

Every sensor reading follows this JSON structure:

```json
{
  "machine_id": "M1",
  "timestamp": 1710000123,
  "temperature": 72.3,
  "vibration": 0.42,
  "rpm": 1450,
  "current": 5.8,
  "pressure": 3.1,
  "humidity": 45.2
}
```

**4 machines monitored:** M1, M2, M3, M4

Each machine has its own baseline — M1 vibration normal ≠ M2 vibration normal. This prevents cross-machine false alarms.

---

## 6. Layer 1: Data Ingestion (Kafka + FastAPI)

### Kafka Producer — Sensor Simulator

```python
# producer/sensor_simulator.py
import random
import time
import json
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

MACHINES = ["M1", "M2", "M3", "M4"]

def generate_reading(machine_id, inject_anomaly=False):
    base = {
        "machine_id": machine_id,
        "timestamp": int(time.time()),
        "temperature": random.uniform(60, 80),
        "vibration": random.uniform(0.2, 0.5),
        "rpm": random.randint(1400, 1600),
        "current": random.uniform(4.5, 6.5),
    }
    if inject_anomaly:
        base["temperature"] = random.uniform(88, 95)   # spike
        base["vibration"] = random.uniform(0.8, 1.2)   # spike
        base["rpm"] = random.randint(1200, 1300)        # drop
    return base

while True:
    for m in MACHINES:
        # Inject anomaly in M2 occasionally for demo
        anomaly = (m == "M2" and random.random() < 0.05)
        data = generate_reading(m, inject_anomaly=anomaly)
        producer.send("machine_stream", data)
    time.sleep(1)
```

### Kafka Consumer

```python
# consumer/kafka_consumer.py
from kafka import KafkaConsumer
import json
from features.feature_engineering import compute_features
from fusion.risk_engine import compute_risk_score
from agent.decision_engine import decide_action

consumer = KafkaConsumer(
    "machine_stream",
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    reading = message.value
    features = compute_features(reading)
    risk = compute_risk_score(features, reading["machine_id"])
    decide_action(reading["machine_id"], risk)
```

---

## 7. Layer 2: Baseline Learning Engine

Each machine gets its own baseline, computed from historical data (last 7 days or last 500 readings).

```python
# models/baseline_builder.py
import numpy as np
import pandas as pd

baselines = {}

def build_baseline(machine_id: str, df: pd.DataFrame):
    """
    df must have columns: temperature, vibration, rpm, current
    """
    baseline = {}
    for col in ["temperature", "vibration", "rpm", "current"]:
        baseline[f"{col}_mean"] = df[col].mean()
        baseline[f"{col}_std"]  = df[col].std()
        baseline[f"{col}_median"] = df[col].median()
        baseline[f"{col}_iqr"]  = df[col].quantile(0.75) - df[col].quantile(0.25)
        # EWMA smoothed baseline
        baseline[f"{col}_ewma"] = df[col].ewm(span=20).mean().iloc[-1]
    baselines[machine_id] = baseline
    return baseline

def get_baseline(machine_id: str):
    return baselines.get(machine_id, {})
```

**Why this matters:** Without per-machine baselines, a normal temperature of 85°C on a furnace motor triggers false alarms on a fan motor where 85°C is catastrophic.

---

## 8. Layer 3: Feature Engineering

Raw readings are transformed into ML-ready signals. This is where the real intelligence begins.

```python
# features/feature_engineering.py
import pandas as pd
import numpy as np
from models.baseline_builder import get_baseline

# In-memory ring buffer per machine (last 50 readings)
buffers = {m: [] for m in ["M1", "M2", "M3", "M4"]}

def compute_features(reading: dict) -> dict:
    mid = reading["machine_id"]
    buf = buffers[mid]
    buf.append(reading)
    if len(buf) > 50:
        buf.pop(0)

    df = pd.DataFrame(buf)
    baseline = get_baseline(mid)
    features = {}

    for col in ["temperature", "vibration", "rpm", "current"]:
        val = reading[col]
        mean = baseline.get(f"{col}_mean", val)
        std  = baseline.get(f"{col}_std", 1)

        # Rolling statistics (window = 5 and 20)
        features[f"{col}_roll_mean_5"]  = df[col].rolling(5).mean().iloc[-1]
        features[f"{col}_roll_std_5"]   = df[col].rolling(5).std().iloc[-1]
        features[f"{col}_roll_mean_20"] = df[col].rolling(20).mean().iloc[-1]

        # Lag features (detect rate of change)
        features[f"{col}_lag1"] = df[col].shift(1).iloc[-1] if len(df) > 1 else val
        features[f"{col}_lag2"] = df[col].shift(2).iloc[-1] if len(df) > 2 else val

        # Rate of change
        features[f"{col}_diff"] = df[col].diff().iloc[-1] if len(df) > 1 else 0

        # Z-score against baseline
        features[f"{col}_zscore"] = (val - mean) / (std + 1e-6)

        # Trend slope (last 10 readings)
        if len(df) >= 10:
            y = df[col].iloc[-10:].values
            x = np.arange(10)
            slope = np.polyfit(x, y, 1)[0]
            features[f"{col}_slope"] = slope
        else:
            features[f"{col}_slope"] = 0

    return features
```

**Summary of features computed per sensor column:**

| Feature | Formula | What it detects |
|---|---|---|
| `roll_mean_5` | mean of last 5 readings | Sudden shift |
| `roll_std_5` | std of last 5 readings | Instability / jitter |
| `lag1`, `lag2` | t-1, t-2 values | Directional trend |
| `diff` | t - (t-1) | Rate of change |
| `zscore` | (val - mean) / std | Deviation from normal |
| `slope` | linear fit on last 10 | Gradual degradation |

---

## 9. Layer 4: Hybrid Anomaly Detection Models

Four detection engines run in parallel on every reading.

### Model 1: Isolation Forest (Unsupervised)

Detects readings that are statistically unusual without needing labelled failures.

```python
# models/isolation_forest.py
from sklearn.ensemble import IsolationForest
import numpy as np

iso_models = {}

def train_iso(machine_id: str, X_train: np.ndarray):
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,  # Expect ~5% anomalies
        random_state=42
    )
    model.fit(X_train)
    iso_models[machine_id] = model

def score_iso(machine_id: str, x: np.ndarray) -> float:
    """Returns 0 (normal) to 1 (anomaly)"""
    model = iso_models.get(machine_id)
    if model is None:
        return 0.0
    pred = model.predict(x.reshape(1, -1))
    # -1 = anomaly, +1 = normal
    return 1.0 if pred[0] == -1 else 0.0
```

### Model 2: XGBoost / Random Forest (Supervised)

Detects compound anomalies — combinations like temperature↑ + vibration↑ + rpm↓.

```python
# models/xgboost_model.py
from xgboost import XGBClassifier
import numpy as np

rf_models = {}

def train_rf(machine_id: str, X_train: np.ndarray, y_train: np.ndarray):
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)
    rf_models[machine_id] = model

def score_rf(machine_id: str, x: np.ndarray) -> float:
    """Returns probability of failure (0 to 1)"""
    model = rf_models.get(machine_id)
    if model is None:
        return 0.0
    prob = model.predict_proba(x.reshape(1, -1))[0][1]
    return float(prob)
```

> **Training labels:** Use synthetic failure events (inject extreme values) or historical failures if available. Label = 1 if failure occurred within next 30 minutes.

### Model 3: Statistical Z-Score Engine

Fast, rule-based spike detection.

```python
# models/stat_engine.py
import numpy as np
from models.baseline_builder import get_baseline

def score_zscore(machine_id: str, reading: dict) -> float:
    """
    Returns max z-score across all sensors, scaled 0–1.
    Score > 0.6 indicates at least one sensor >3σ from normal.
    """
    baseline = get_baseline(machine_id)
    max_z = 0.0
    for col in ["temperature", "vibration", "rpm", "current"]:
        mean = baseline.get(f"{col}_mean", reading[col])
        std  = baseline.get(f"{col}_std", 1)
        z = abs((reading[col] - mean) / (std + 1e-6))
        max_z = max(max_z, z)

    # Scale: z=3 → 0.6, z=5 → 1.0
    return min(max_z / 5.0, 1.0)
```

### Model 4: LSTM Autoencoder (Temporal)

Detects gradual degradation patterns over time that instantaneous models miss.

```python
# models/lstm_autoencoder.py
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model

lstm_models = {}
SEQUENCE_LEN = 20

def build_lstm_autoencoder(n_features: int):
    inp = tf.keras.Input(shape=(SEQUENCE_LEN, n_features))
    # Encoder
    x = layers.LSTM(32, activation='relu', return_sequences=False)(inp)
    bottleneck = layers.Dense(8)(x)
    # Decoder
    x = layers.RepeatVector(SEQUENCE_LEN)(bottleneck)
    x = layers.LSTM(32, activation='relu', return_sequences=True)(x)
    out = layers.TimeDistributed(layers.Dense(n_features))(x)
    model = Model(inputs=inp, outputs=out)
    model.compile(optimizer='adam', loss='mse')
    return model

def train_lstm(machine_id: str, X_sequences: np.ndarray):
    model = build_lstm_autoencoder(X_sequences.shape[2])
    model.fit(X_sequences, X_sequences, epochs=20, batch_size=32, verbose=0)
    lstm_models[machine_id] = model

def score_lstm(machine_id: str, sequence: np.ndarray) -> float:
    """
    sequence shape: (1, SEQUENCE_LEN, n_features)
    Returns reconstruction error scaled 0–1.
    """
    model = lstm_models.get(machine_id)
    if model is None:
        return 0.0
    reconstructed = model.predict(sequence, verbose=0)
    error = np.mean((sequence - reconstructed) ** 2)
    # Scale by empirical threshold (tune per machine)
    return min(error / 0.1, 1.0)
```

---

## 10. Layer 5: Risk Score Fusion Engine

All 4 model outputs are fused into a single risk score.

```python
# fusion/risk_engine.py
from models.isolation_forest import score_iso
from models.xgboost_model import score_rf
from models.stat_engine import score_zscore
from models.lstm_autoencoder import score_lstm
import numpy as np

# Weights must sum to 1.0
WEIGHTS = {
    "rf":   0.40,
    "iso":  0.30,
    "z":    0.20,
    "lstm": 0.10
}

def compute_risk_score(features: dict, machine_id: str, reading: dict,
                       sequence: np.ndarray = None) -> dict:
    x = np.array(list(features.values()))

    rf_score   = score_rf(machine_id, x)
    iso_score  = score_iso(machine_id, x)
    z_score    = score_zscore(machine_id, reading)
    lstm_score = score_lstm(machine_id, sequence) if sequence is not None else 0.0

    risk = (
        WEIGHTS["rf"]   * rf_score  +
        WEIGHTS["iso"]  * iso_score +
        WEIGHTS["z"]    * z_score   +
        WEIGHTS["lstm"] * lstm_score
    )

    return {
        "risk_score":   round(risk, 4),
        "rf_score":     round(rf_score, 4),
        "iso_score":    round(iso_score, 4),
        "z_score":      round(z_score, 4),
        "lstm_score":   round(lstm_score, 4),
        "severity":     classify_severity(risk)
    }

def classify_severity(score: float) -> str:
    if score < 0.30:
        return "LOW"
    elif score < 0.60:
        return "MEDIUM"
    elif score < 0.80:
        return "HIGH"
    else:
        return "CRITICAL"
```

**Severity thresholds:**

| Risk Score | Severity | Meaning |
|---|---|---|
| 0.00 – 0.29 | LOW | Normal — log only |
| 0.30 – 0.59 | MEDIUM | Watch — dashboard alert |
| 0.60 – 0.79 | HIGH | Warning — SMS |
| 0.80 – 1.00 | CRITICAL | Failure imminent — voice call + ticket |

---

## 11. Layer 6: Agent Decision Engine

This is what makes the system **agentic** — it observes, reasons, and acts autonomously.

```python
# agent/decision_engine.py
from alerts.sms_service import send_sms
from alerts.voice_service import trigger_voice_call
from database.db import log_event, create_incident_ticket
from api.dashboard import push_dashboard_alert
from maintenance.scheduler import schedule_maintenance
import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0)
COOLDOWN_SECONDS = 300  # 5 min cooldown per machine to prevent alert storms

def decide_action(machine_id: str, risk: dict):
    severity  = risk["severity"]
    score     = risk["risk_score"]
    cooldown_key = f"cooldown:{machine_id}"

    # Always log
    log_event(machine_id, risk)

    # Check cooldown (prevent alert storms)
    if r.exists(cooldown_key) and severity in ["MEDIUM", "HIGH"]:
        return

    if severity == "LOW":
        return  # Just log

    elif severity == "MEDIUM":
        push_dashboard_alert(machine_id, risk)
        r.setex(cooldown_key, COOLDOWN_SECONDS, 1)

    elif severity == "HIGH":
        push_dashboard_alert(machine_id, risk)
        send_sms(machine_id, risk)
        r.setex(cooldown_key, COOLDOWN_SECONDS, 1)
        schedule_maintenance(machine_id, hours=12)

    elif severity == "CRITICAL":
        push_dashboard_alert(machine_id, risk)
        send_sms(machine_id, risk)
        trigger_voice_call(machine_id, risk)
        create_incident_ticket(machine_id, risk)
        schedule_maintenance(machine_id, hours=0)  # Immediate
        r.setex(cooldown_key, COOLDOWN_SECONDS * 2, 1)
```

### State Machine

The agent maintains a per-machine state machine:

```
Normal ──(risk > 0.3)──► Watch ──(risk > 0.6)──► Warning ──(risk > 0.8)──► Critical
  ▲                         │                         │                         │
  └────────(risk drops)─────┘─────────────────────────┘─────────────────────────┘
```

N-of-M suppression: only elevate state if M anomalies detected in last N readings (prevents single-sample false alarms).

---

## 12. Smart Alert & Escalation System

```
Input (ML Engine)
  Anomaly Score
  Trend Data          ──► Alert Engine ──► Severity Check ──► Escalation Logic
  Machine Context          Receive Event        │
                           Validate & Filter    ├── LOW      → Log Only
                           Compute Severity     ├── MEDIUM   → Web Dashboard Notification
                           Generate Alert       ├── HIGH     → Dashboard + In-App + SMS
                           (type, score, reason)└── CRITICAL → Dashboard + SMS + Call + Ticket
```

**Notification channels per severity:**

| Severity | Dashboard | In-App Toast | SMS (Twilio) | Voice Call (Twilio) | Incident Ticket |
|---|---|---|---|---|---|
| LOW | ✅ (log tab) | ❌ | ❌ | ❌ | ❌ |
| MEDIUM | ✅ | ✅ | ❌ | ❌ | ❌ |
| HIGH | ✅ | ✅ | ✅ | ❌ | ❌ |
| CRITICAL | ✅ | ✅ | ✅ | ✅ | ✅ |

**Engineer action flow:**
1. View Alert & Details
2. Acknowledge Alert
3. Take Action
4. Update Status

---

## 13. Explainable AI (XAI) Layer

Every alert must include a human-readable explanation. Example output:

```
Machine M2 — CRITICAL ALERT
Risk Score: 0.87

Reasons detected:
  • Vibration increased 42% above normal baseline
  • Temperature rising steadily for last 10 minutes (slope: +0.8°C/min)
  • RPM dropped 12% below expected range
  • Compound anomaly: all 3 sensors degrading simultaneously

Predicted failure type: Bearing deterioration
Failure probability: 87%
Recommended action: Immediate inspection — shutdown within 2 hours
```

```python
# agent/explainer.py
from models.baseline_builder import get_baseline

def generate_explanation(machine_id: str, reading: dict, features: dict, risk: dict) -> str:
    baseline = get_baseline(machine_id)
    reasons = []

    for col in ["temperature", "vibration", "rpm", "current"]:
        z = features.get(f"{col}_zscore", 0)
        slope = features.get(f"{col}_slope", 0)
        mean = baseline.get(f"{col}_mean", reading[col])
        val = reading[col]
        pct_change = ((val - mean) / (mean + 1e-6)) * 100

        if abs(z) > 3:
            direction = "above" if val > mean else "below"
            reasons.append(
                f"{col.capitalize()} is {abs(pct_change):.1f}% {direction} normal baseline"
            )
        if abs(slope) > 0.5:
            direction = "rising" if slope > 0 else "falling"
            reasons.append(
                f"{col.capitalize()} is {direction} steadily (slope: {slope:+.2f}/reading)"
            )

    compound = sum(1 for c in ["temperature", "vibration", "rpm", "current"]
                   if abs(features.get(f"{c}_zscore", 0)) > 2)
    if compound >= 3:
        reasons.append("Compound anomaly: multiple sensors degrading simultaneously")

    explanation = f"Machine {machine_id} — {risk['severity']} ALERT\n"
    explanation += f"Risk Score: {risk['risk_score']}\n\n"
    explanation += "Reasons detected:\n"
    for r in reasons:
        explanation += f"  • {r}\n"

    return explanation
```

---

## 14. Backend API Structure (FastAPI)

```python
# api/main.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio, json

app = FastAPI(title="Predictive Maintenance API")

@app.get("/stream/{machine_id}")
async def stream_sensor(machine_id: str):
    """Server-Sent Events — live sensor readings"""
    async def event_gen():
        while True:
            data = get_latest_reading(machine_id)
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(event_gen(), media_type="text/event-stream")

@app.get("/history/{machine_id}")
def get_history(machine_id: str, limit: int = 200):
    return fetch_history(machine_id, limit)

@app.get("/machine-status")
def all_machine_status():
    return get_all_machine_statuses()

@app.post("/alert")
def create_alert(alert: dict):
    save_alert_to_db(alert)
    return {"status": "saved"}

@app.get("/alerts")
def list_alerts(machine_id: str = None, severity: str = None):
    return fetch_alerts(machine_id, severity)

@app.post("/schedule-maintenance")
def schedule(payload: dict):
    return schedule_maintenance(payload["machine_id"], payload["hours"])

@app.get("/risk/{machine_id}")
def current_risk(machine_id: str):
    return get_current_risk(machine_id)
```

---

## 15. Database Schema (PostgreSQL)

```sql
-- database/schema.sql

CREATE TABLE machines (
    machine_id      VARCHAR(10) PRIMARY KEY,
    name            VARCHAR(100),
    location        VARCHAR(100),
    machine_type    VARCHAR(50),
    status          VARCHAR(20) DEFAULT 'HEALTHY',
    last_seen       TIMESTAMP
);

CREATE TABLE sensor_data (
    id              SERIAL PRIMARY KEY,
    machine_id      VARCHAR(10) REFERENCES machines(machine_id),
    timestamp       BIGINT NOT NULL,
    temperature     FLOAT,
    vibration       FLOAT,
    rpm             INT,
    current         FLOAT,
    pressure        FLOAT,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alerts (
    alert_id        SERIAL PRIMARY KEY,
    machine_id      VARCHAR(10) REFERENCES machines(machine_id),
    risk_score      FLOAT NOT NULL,
    severity        VARCHAR(20) NOT NULL,
    rf_score        FLOAT,
    iso_score       FLOAT,
    z_score         FLOAT,
    lstm_score      FLOAT,
    reason          TEXT,
    acknowledged    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE incidents (
    incident_id     SERIAL PRIMARY KEY,
    machine_id      VARCHAR(10) REFERENCES machines(machine_id),
    alert_id        INT REFERENCES alerts(alert_id),
    description     TEXT,
    status          VARCHAR(20) DEFAULT 'OPEN',
    assigned_to     VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW(),
    resolved_at     TIMESTAMP
);

CREATE TABLE maintenance_schedule (
    id              SERIAL PRIMARY KEY,
    machine_id      VARCHAR(10) REFERENCES machines(machine_id),
    scheduled_at    TIMESTAMP NOT NULL,
    urgency         VARCHAR(20),
    reason          TEXT,
    completed       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE calls (
    call_id         SERIAL PRIMARY KEY,
    machine_id      VARCHAR(10),
    twilio_sid      VARCHAR(100),
    status          VARCHAR(20),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_sensor_machine ON sensor_data(machine_id, timestamp DESC);
CREATE INDEX idx_alerts_machine ON alerts(machine_id, created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity);
```

---

## 16. Frontend Dashboard (Next.js)

**Key pages and components:**

```
/dashboard
  ├── MachineGrid         — 4 machine cards with live status
  ├── RiskGauge           — Animated risk score 0-100
  ├── SensorChart         — Real-time line charts (SSE)
  ├── AlertFeed           — Live alert stream
  └── MaintenanceTimeline — Upcoming scheduled work

/alerts
  ├── AlertTable          — Filterable by machine, severity, time
  └── AlertDetail         — Full explanation + action buttons

/history/{machine_id}
  └── Historical sensor charts + anomaly markers
```

**Live data via SSE:**

```javascript
// hooks/useSensorStream.js
import { useEffect, useState } from 'react'

export function useSensorStream(machineId) {
  const [data, setData] = useState(null)

  useEffect(() => {
    const es = new EventSource(`/api/stream/${machineId}`)
    es.onmessage = (e) => setData(JSON.parse(e.data))
    return () => es.close()
  }, [machineId])

  return data
}
```

**Machine status display:**

```
Machine M1 → 🟢 HEALTHY     (risk: 0.12)
Machine M2 → 🟡 WARNING     (risk: 0.54)
Machine M3 → 🔴 CRITICAL    (risk: 0.91)
Machine M4 → 🟢 HEALTHY     (risk: 0.08)
```

---

## 17. Async Jobs (Redis + Celery)

Long-running tasks (SMS, calls, ticket creation) are offloaded to Celery workers.

```python
# celery_app.py
from celery import Celery

app = Celery('maintenance', broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')

@app.task
def async_send_sms(machine_id: str, risk: dict):
    from alerts.sms_service import send_sms
    send_sms(machine_id, risk)

@app.task
def async_trigger_call(machine_id: str, risk: dict):
    from alerts.voice_service import trigger_voice_call
    trigger_voice_call(machine_id, risk)

@app.task
def async_create_ticket(machine_id: str, risk: dict):
    from database.db import create_incident_ticket
    create_incident_ticket(machine_id, risk)
```

**Start workers:**
```bash
celery -A celery_app worker --loglevel=info --concurrency=4
```

---

## 18. Voice Alert System (Twilio + ElevenLabs)

### SMS (Twilio)

```python
# alerts/sms_service.py
from twilio.rest import Client
import os

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

def send_sms(machine_id: str, risk: dict):
    msg = (
        f"⚠️ MAINTENANCE ALERT\n"
        f"Machine {machine_id} — {risk['severity']}\n"
        f"Risk Score: {risk['risk_score']:.2f}\n"
        f"Action required immediately."
    )
    client.messages.create(
        body=msg,
        from_=os.getenv("TWILIO_FROM"),
        to=os.getenv("ENGINEER_PHONE")
    )
```

### Voice Call (Twilio + ElevenLabs)

```python
# alerts/voice_service.py
from twilio.rest import Client
from elevenlabs import generate, Voice
import os, base64

twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

def trigger_voice_call(machine_id: str, risk: dict):
    # Generate spoken explanation via ElevenLabs
    script = (
        f"Critical maintenance alert. Machine {machine_id} has a risk score of "
        f"{risk['risk_score']:.2f}. Immediate inspection is required. "
        f"The system has detected {risk.get('reason', 'multiple sensor anomalies')}. "
        f"Please acknowledge this alert on the dashboard."
    )

    # ElevenLabs TTS
    audio = generate(
        text=script,
        voice=Voice(voice_id=os.getenv("ELEVENLABS_VOICE_ID")),
        api_key=os.getenv("ELEVENLABS_API_KEY")
    )

    # Save audio and serve via public URL (upload to S3 or use ngrok for demo)
    audio_url = upload_audio_to_storage(audio)

    # Twilio outbound call with TwiML
    twiml = f'<Response><Play>{audio_url}</Play></Response>'
    twilio_client.calls.create(
        twiml=twiml,
        from_=os.getenv("TWILIO_FROM"),
        to=os.getenv("ENGINEER_PHONE")
    )
```

---

## 19. Maintenance Scheduler

```python
# maintenance/scheduler.py
from datetime import datetime, timedelta
from database.db import db_session
from database.models import MaintenanceSchedule

URGENCY_MAP = {
    0:   "IMMEDIATE",
    12:  "URGENT",
    48:  "SCHEDULED",
    168: "ROUTINE"
}

def schedule_maintenance(machine_id: str, hours: int):
    scheduled_at = datetime.utcnow() + timedelta(hours=hours)
    urgency = URGENCY_MAP.get(hours, "SCHEDULED")

    record = MaintenanceSchedule(
        machine_id=machine_id,
        scheduled_at=scheduled_at,
        urgency=urgency,
        reason=f"Auto-scheduled by predictive maintenance agent"
    )
    db_session.add(record)
    db_session.commit()
    return {"scheduled_at": scheduled_at.isoformat(), "urgency": urgency}
```

**Scheduling logic:**

| Severity | Action | Scheduled In |
|---|---|---|
| LOW | No action | — |
| MEDIUM | Dashboard only | — |
| HIGH | SMS + schedule | 12 hours |
| CRITICAL | Call + ticket + schedule | Immediate (0 hours) |

---

## 20. Full Folder Structure

```
predictive-maintenance-agent/
│
├── producer/
│   └── sensor_simulator.py          # Kafka sensor data generator
│
├── consumer/
│   └── kafka_consumer.py            # Reads from Kafka, triggers pipeline
│
├── features/
│   └── feature_engineering.py       # Rolling stats, z-scores, lag, slope
│
├── models/
│   ├── baseline_builder.py          # Per-machine baseline (mean/std/EWMA)
│   ├── isolation_forest.py          # Unsupervised anomaly detection
│   ├── xgboost_model.py             # Supervised compound anomaly detection
│   ├── stat_engine.py               # Z-score threshold engine
│   └── lstm_autoencoder.py          # Temporal sequence anomaly detection
│
├── fusion/
│   └── risk_engine.py               # Weighted fusion → single risk score
│
├── agent/
│   ├── decision_engine.py           # Agentic: observe → decide → act
│   ├── explainer.py                 # Human-readable alert explanations
│   └── state_machine.py             # Per-machine state: Normal→Watch→Critical
│
├── alerts/
│   ├── sms_service.py               # Twilio SMS
│   └── voice_service.py             # Twilio + ElevenLabs voice call
│
├── maintenance/
│   └── scheduler.py                 # Auto maintenance scheduling
│
├── api/
│   └── main.py                      # FastAPI endpoints
│
├── database/
│   ├── schema.sql                   # PostgreSQL tables
│   ├── db.py                        # DB connection + helpers
│   └── models.py                    # SQLAlchemy ORM models
│
├── celery_app.py                    # Celery async task queue
│
├── dashboard/                       # Next.js frontend
│   ├── pages/
│   │   ├── index.js                 # Machine overview
│   │   ├── alerts.js                # Alert management
│   │   └── history/[machine_id].js  # Historical data
│   ├── components/
│   │   ├── MachineCard.jsx
│   │   ├── RiskGauge.jsx
│   │   └── SensorChart.jsx
│   └── hooks/
│       └── useSensorStream.js       # SSE hook
│
├── .env                             # API keys (never commit)
├── requirements.txt                 # Python dependencies
├── package.json                     # Node dependencies
└── docker-compose.yml               # Kafka + Redis + PostgreSQL
```

---

## 21. Tech Stack Summary

| Component | Technology | Purpose |
|---|---|---|
| Streaming | Apache Kafka | Real-time sensor data pipeline |
| Backend | FastAPI (Python) | REST API + SSE streaming |
| ML Models | scikit-learn, XGBoost | Isolation Forest + Random Forest |
| Deep Learning | TensorFlow/Keras | LSTM Autoencoder |
| Async Queue | Redis + Celery | Non-blocking alert jobs |
| Storage | PostgreSQL | Alerts, incidents, sensor history |
| Frontend | Next.js + React | Live dashboard |
| SMS | Twilio | Alert SMS to engineers |
| Voice | Twilio + ElevenLabs | Spoken CRITICAL alerts |
| Containerisation | Docker Compose | Local dev environment |

**Python requirements.txt:**
```
fastapi
uvicorn
kafka-python
scikit-learn
xgboost
tensorflow
numpy
pandas
redis
celery
psycopg2-binary
sqlalchemy
twilio
elevenlabs
python-dotenv
```

**Docker Compose (infrastructure):**
```yaml
# docker-compose.yml
version: "3.8"
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on: [zookeeper]
    ports: ["9092:9092"]
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: maintenance
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    ports: ["5432:5432"]

  redis:
    image: redis:7
    ports: ["6379:6379"]
```

---

## 22. End-to-End Demo Flow (Hackathon)

**What to demonstrate in sequence:**

1. **Start infrastructure**
   ```bash
   docker-compose up -d
   ```

2. **Start sensor simulator**
   ```bash
   python producer/sensor_simulator.py
   ```
   → 4 machines stream data every second

3. **Start backend**
   ```bash
   uvicorn api.main:app --reload
   celery -A celery_app worker --loglevel=info
   ```

4. **Open dashboard** → show all 4 machines HEALTHY (green)

5. **Inject anomaly** into M2 (flip the flag in simulator)
   → Within 5–10 seconds:
   - M2 risk score rises 0.12 → 0.54 → 0.87
   - Dashboard card turns yellow → orange → red
   - Alert appears in feed with full explanation
   - SMS sent to engineer's phone
   - Outbound voice call triggers with ElevenLabs spoken alert
   - Incident ticket created in PostgreSQL
   - Maintenance scheduled as IMMEDIATE

6. **Show explanation text:**
   ```
   Machine M2 — CRITICAL
   • Vibration 42% above baseline
   • Temperature rising at +0.8°C/min
   • Compound anomaly across 3 sensors
   Predicted: Bearing failure — 87% probability
   ```

7. **Acknowledge** on dashboard → status updated

**Judging checklist:**

| Criteria | Demonstrated by |
|---|---|
| Real-time pipeline | Live Kafka stream on dashboard |
| Hybrid AI detection | 4-model fusion risk score |
| Explainability | Natural-language alert reason |
| Agentic behaviour | Auto-escalation without human input |
| Multi-machine support | 4 machines simultaneously |
| Alert automation | SMS + voice triggered live |

---

## 23. References

**Research Papers:**
- Liu, F. T., et al. (2008). *Isolation Forest*. IEEE ICDM. https://ieeexplore.ieee.org/document/4781136
- Malhotra, P., et al. (2016). *LSTM-based Encoder-Decoder for Anomaly Detection*. arXiv. https://arxiv.org/abs/1607.00148

**Tools & APIs:**
- Twilio Voice & SMS — https://twilio.com/docs
- ElevenLabs Voice AI — https://elevenlabs.io/docs
- Next.js — https://nextjs.org/docs
- FastAPI — https://fastapi.tiangolo.com
- Redis — https://redis.io/docs
- Celery — https://docs.celeryq.dev
- PostgreSQL — https://postgresql.org/docs
- Apache Kafka — https://kafka.apache.org/documentation

**Industry Insight:**
- McKinsey & Company. *Predictive Maintenance and AI in Manufacturing*. https://www.mckinsey.com/capabilities/operations/our-insights/industry-40-reimagining-manufacturing-operations-after-covid-19

---

*Document prepared for Team beyondminus | Hack Malenadu Hackathon*  
*Predictive Maintenance Agent — Complete Technical Build Guide*
