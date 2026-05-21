# 🤖 PredictAI — Autonomous Agentic Predictive Maintenance System

[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15%20%2F%2016-black?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-3.6.0-red?logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%20%7C%2016-blue?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7.0-red?logo=redis&logoColor=white)](https://redis.io/)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost%20%7C%20scikit--learn-orange?logo=scikitlearn&logoColor=white)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

**Team:** beyondminus | **Hackathon:** Hack Malenadu 2026  
**Developers:** Mallikarjun Paroji · Jeet Mundra · Vraj Joisar · Sumanth KS

---

## 💡 Executive Summary

**PredictAI** is a closed-loop, high-availability autonomous agent system designed to solve the **"Trillion-Dollar Problem"** of unexpected industrial machinery downtime. 

Traditional factory maintenance is either reactive (repairing after a failure occurs) or scheduled (servicing at static intervals, which is costly and inefficient). PredictAI shifts this paradigm to **Streaming Sensor Analytics**. By ingesting high-frequency telemetry, running an ensemble machine learning brain, and executing automated mitigation protocols (AI-synthesized voice calls, emergency SMS, and database maintenance ticket scheduling), PredictAI intercepts mechanical degradation minutes before failure, ensuring zero downtime and fully autonomous operation.

---

## 🏗️ System Architecture & Data Flow

PredictAI is designed as a modular microservices pipeline capable of handling thousands of telemetry events per second:

```mermaid
graph TD
    subgraph "Data Ingestion Layer"
        SS[Official Machine Server <br/> SSE Stream] -->|1. SSE Stream Client| SC[stream_client.py]
        TS[Local Telemetry Simulator] -->|Alternative Source| KP[Kafka Producer]
        SC -->|2. Buffer Readings| KB[Apache Kafka Broker]
    end

    subgraph "State & Caching Layer"
        KB -->|3. Consume Readings| KC[Kafka Consumer]
        KC -->|Publish Status| RD[(Redis Cache)]
        KC -->|Log Alerts & Events| PG[(PostgreSQL Database)]
    end

    subgraph "Intelligence Matrix (The Brain)"
        KC -->|4. Feature Vector| AE[Agent Inference Engine]
        AE -->|Statistical Outliers| ZS[Dynamic Z-Scores]
        AE -->|Spatial Anomalies| IF[Isolation Forest]
        AE -->|Failure Mode Classification| XGB[XGBoost Classifier]
        AE -->|Temporal Degradation| LSTM[LSTM Autoencoder]
        
        ZS & IF & XGB & LSTM -->|5. Probability Scores| DF[Decision Fusion Scorer]
    end

    subgraph "Autonomous Mitigation Loop"
        DF -->|6. Calculate Risk Score| DE[Decision Engine]
        DE -->|Risk > 0.8 / Critical| VC[Twilio Voice Call <br/> + ElevenLabs AI Synthesizer]
        DE -->|Risk > 0.6 / High| SMS[Twilio SMS Alert]
        DE -->|Auto-Mitigate| WEB[Schedule Maintenance Webhook]
        
        RD -->|Sub-second UI Sync| DB[Next.js Glassmorphism Dashboard]
        PG -->|Fetch Historic Tickets| DB
    end
```

### Infrastructure Stack Components:
1. **Ingestion Bridge**: Persistent connection to the factory Server-Sent Events (SSE) server. 
2. **Apache Kafka**: Acts as an message broker to prevent telemetry loss during network spikes or high-throughput scenarios.
3. **Inference & Decision Engine**: Headless consumer workers that continuously compute rolling statistics, feed features to ML models, and fuse scores.
4. **Redis Cache**: Holds the latest machine status for sub-millisecond frontend fetches and implements "Alert Cooldown Lockout" logic.
5. **PostgreSQL 15**: Serves as the single source of truth for persistent, auditable incident tickets and alert histories.
6. **Next.js 16 Dashboard**: Glassmorphic, real-time command center displaying live sensor graphs, AI confidence status, and incident tracking tables.

---

## 🧠 The Intelligence Core (Decision Fusion)

To minimize costly false positives while ensuring 100% anomaly detection, PredictAI uses a **Triple-Defense Ensemble Engine**:

### 1. Dynamic Statistical Baselines (Z-Score)
* **Goal**: Identify immediate "Out-of-Bounds" spikes or gradual drifts.
* **Mechanism**: Calibrated using a baseline historical dataset ($10,080$ records per machine). It computes machine-specific rolling mean ($\mu$) and standard deviation ($\sigma$).
* **Mathematical Formula**:
  $$Z = \frac{x - \mu}{\sigma}$$
* **Threshold**: Flags values deviating by $|Z| > 3.5$.

### 2. Unsupervised Spatial Outliers (Isolation Forest)
* **Goal**: Detect "Unknown Unknowns" — complex multi-sensor anomalies that are within individual thresholds but structurally abnormal.
* **Mechanism**: Isolates observations in $N$-dimensional space by splitting random features. Unusual combinations of variables (e.g., normal temperature but unusually low RPM and high vibration) are isolated quickly, returning high anomaly scores.

### 3. Supervised Failure Classification (XGBoost)
* **Goal**: Categorize and confirm known mechanical failure profiles.
* **Target Signatures**: Trained to recognize specific patterns:
  * **Thermal Runaway (CNC Mill)**: Fast rise in temp, current instability, followed by a sudden speed drop.
  * **Pump Cavitation**: Sudden RPM collapse accompanied by high electrical current surge.
  * **Bearing Wear**: Rising vibration harmonics over time.

### 4. Temporal Degradation Tracking (LSTM Autoencoder)
* **Goal**: Identify slow, long-term degradation patterns.
* **Mechanism**: Neural network model that learns to reconstruct normal operational sequences. High reconstruction error indicates temporal structural decay.

### Weighted Risk Fusion:
The decision engine fuses these models using a weighted scoring formula to produce a normalized Risk Score between `0.0` (Healthy) and `1.0` (Failure Imminent):
$$\text{Risk Score} = 0.4 \times S_{\text{XGBoost}} + 0.3 \times S_{\text{IsolationForest}} + 0.3 \times S_{\text{Z-Score}}$$

---

## 🚨 Mitigation & Escalation Protocol

The system maintains a fully autonomous response pipeline mapped to the fused risk score. An **Explainable AI (XAI)** module translates raw probabilities into plain-English root causes, which are then transmitted to field engineers.

| Risk Score | Severity | UI Color | Executed Actions |
| :--- | :--- | :--- | :--- |
| **< 0.3** | **LOW** | Green (Healthy) | Passive background logging to PostgreSQL. |
| **0.3 - 0.6** | **MEDIUM** | Yellow (Warning) | Real-time Dashboard alert, status update, and Redis cooldown key set. |
| **0.6 - 0.8** | **HIGH** | Orange (Alert) | Twilio SMS notification sent to engineer, `/alert` webhook sent to central servers, auto-scheduling maintenance request for the next 12 hours. |
| **> 0.8** | **CRITICAL** | Red (Emergency) | **AI Voice Call** (ElevenLabs synthesized text-to-speech engine + Twilio Voice), immediate `/schedule-maintenance` API push, and persistent incident ticket created. |

> 🛡️ **Alert Cooldown System**: To prevent "notification storms" (spamming an engineer with hundreds of text messages for a rapid telemetry stream), PredictAI utilizes Redis cache keys to lock out duplicate alerts for 5 minutes (`COOLDOWN_SECONDS = 300`) after an escalation.

---

## ⚙️ Configuration & Setup

### Prerequisites
* **Docker & Docker Compose** installed
* **Python 3.10+** environment
* **Node.js 18+** (for frontend development)

### 1. Clone & Set Up Directory
Ensure you are in the project root:
```bash
# Clone the repository
git clone https://github.com/jeetmundra/Malenadu1.git
cd Malenadu1
```

### 2. Configure Environment Variables
Copy the template configuration and input your API credentials:
```bash
cp .env.example .env
```
Inside your `.env` file, configure the following keys:
```env
# Database & Cache Configurations
DATABASE_URL=postgresql://admin:secret@localhost:5432/maintenance
REDIS_URL=redis://localhost:6379/0

# Twilio (SMS & Voice Alerts)
TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM=+12345678901
ENGINEER_PHONE=+919876543210 # Your phone number to receive alerts

# ElevenLabs (AI Text-to-Speech)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here

# Message Broker
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Hackathon Server Endpoint
HACKATHON_API_URL=http://localhost:3000
```

### 3. Spin Up Infrastructure
Launch the Docker containers for Zookeeper, Kafka, Redis, and PostgreSQL:
```bash
docker-compose up -d
```

### 4. Install Python Dependencies
Create a virtual environment and install the required machine learning and communication libraries:
```bash
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate # On macOS/Linux

pip install -r requirements.txt
```

---

## 🚀 Running the Services

You can start the backend services simultaneously using the pre-configured script or manually in separate terminal windows:

### Option A: The Windows Startup Script (Recommended)
```bash
start_backend.bat
```
This bat file automatically spins up four terminals, activates the virtual environments, and starts the following components.

### Option B: Manual Execution
If executing manually, open four separate terminals and run:

* **Terminal 1: Telemetry Sensor Simulator (Kafka Producer)**
  Generates streaming data representing the operations of 4 industrial machines (`CNC_01`, `CNC_02`, `PUMP_03`, `CONVEYOR_04`).
  ```bash
  python producer/sensor_simulator.py
  ```

* **Terminal 2: Core ML Pipeline (Kafka Consumer & Scorer)**
  Ingests raw telemetry, applies Z-Score, Isolation Forest, and XGBoost, and forwards fused anomaly flags to the database.
  ```bash
  python consumer/kafka_consumer.py
  ```

* **Terminal 3: FastAPI Backend**
  Exposes REST APIs and SSE (Server-Sent Events) streaming interfaces to push real-time status updates to the dashboard.
  ```bash
  uvicorn api.main:app --reload --port 8000
  ```

* **Terminal 4: Celery Worker Queue**
  Asynchronously handles the outbound Twilio calls and ElevenLabs AI Voice synthesis to keep the telemetry consumer latency low.
  ```bash
  celery -A celery_app worker --loglevel=info
  ```

---

## 🖥️ Starting the Next.js Dashboard

The frontend command center is located in the `/dashboard` directory. It uses Next.js and Tailwind CSS for a premium dark mode, glassmorphic UI.

```bash
cd dashboard
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) on your browser to view the Command Center.

---

## ⚡ Live Hackathon Demo Walkthrough

To verify and demonstrate the autonomous agent pipeline in real-time, follow these steps:

1. **System Health Check**: Verify that all services are online. Open the Next.js Dashboard (`http://localhost:3000`). All four machinery cards should display **HEALTHY** (Green) with risk scores hovering below `0.15`.
2. **Baseline Stability**: Observe the rolling charts showing live sensor telemetry (RPM, Temperature, Current, Vibration) streaming at $1$ reading per second.
3. **Triggering Anomaly Ingestion**: On the dashboard UI, click the **"⚡ Inject Anomaly"** button next to Machine `CNC_02` (Thermal Runaway simulation).
4. **Real-time Anomaly Tracking**:
   * Watch the telemetry graph show a sharp rise in temperature and current.
   * The **Decision Fusion Engine** recalculates live: Risk score rises: `0.12 → 0.45 (MEDIUM) → 0.72 (HIGH) → 0.92 (CRITICAL)`.
5. **Dashboard State Update**: The machine card transitions from Green to **Yellow**, then **Orange**, and finally **Red**. The Explainable AI panel updates:  
   > *“Anomaly detected on CNC_02: Temperature above baseline (78.2°C vs baseline 54.1°C), power current spike detected.”*
6. **Triggering the Outreach Engine**:
   * An **SMS alert** lands on the engineer's phone detailing the exact machine ID and reasoning.
   * A **phone call** triggers, reading the synthesized text-to-speech breakdown explanation via ElevenLabs.
7. **Self-Healing Webhook (Auto-Mitigation)**: The agent posts a request to the `/schedule-maintenance` API. On the Next.js UI, the machine ticket transitions to a pending maintenance state, resetting the risk score and simulating successful repair scheduler execution.

---

## 📂 Project Directory Structure

```
Malenadu1/
├── producer/                 # Kafka sensor simulator (4 machines)
│   └── sensor_simulator.py   # Simulates live factory telemetry
├── consumer/                 # Kafka consumer → ML pipeline
│   └── kafka_consumer.py     # Aggregates telemetry & triggers evaluation
├── features/                 # Feature engineering engine (rolling slopes, lag)
├── models/                   # Mathematical & AI Models
│   ├── baseline_builder.py   # Calibrates dynamic baseline mean/std
│   ├── stat_engine.py        # Computes live Z-Score deviations
│   ├── isolation_forest.py   # Unsupervised outlier scoring
│   ├── xgboost_model.py      # Supervised breakdown classifier
│   └── lstm_autoencoder.py   # Neural temporal degradation tracking
├── agent/                    # Decision & Explanation Layer
│   ├── decision_engine.py    # Determines escalation level & cooldowns
│   └── explainer.py          # Generates natural language root causes (XAI)
├── alerts/                   # Notification & Outreach Handlers
│   ├── sms_service.py        # Twilio SMS pipeline
│   └── voice_service.py      # ElevenLabs & Twilio Voice synthesized calls
├── maintenance/              # Automated scheduler routines
│   └── scheduler.py          # Schedules ticket tasks & repair slots
├── api/                      # FastAPI Backend
│   └── main.py               # Exposes SSE Streams and REST Endpoints
├── database/                 # Relational Schema & ORM Layer
│   ├── db.py                 # DB connection and session instantiator
│   └── models.py             # Alert and Incident SQL tables
├── dashboard/                # Next.js 16 Glassmorphism Dashboard
│   ├── src/                  # React components & UI logic
│   └── package.json          # Node dependencies
├── docker-compose.yml        # Infrastructure setup (Kafka, Redis, Postgres)
├── start_backend.bat         # Single-click backend orchestration scripts
├── requirements.txt          # Python dependencies
└── .env.example              # Environment variables template
```

---

## 🏆 Presentation Highlights (For Evaluators)

When showcasing this project for placements or interviewers, emphasize the following high-level engineering decisions:
* **Microservice Decoupling**: Raw sensor ingest is fully separated from model inference, using Kafka as a highly reliable buffer.
* **Explainable AI (XAI)**: Showing how raw numerical outputs of neural networks and ensemble models are parsed into human-friendly messages.
* **Notification Cooldown**: Explaining how the Redis caching layer protects the notification system from flooding field technicians during a crash.
* **Micro-transaction Mitigation**: Demonstrating that the system acts on its predictions by scheduling its own maintenance rather than just creating static charts.
