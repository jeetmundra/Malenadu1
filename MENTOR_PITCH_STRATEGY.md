# 🎯 Mentor Round 1: Scoring Strategy & Pitch Guide

Use this document to maximize your score during the first evaluation round. It maps our technical implementation directly to the 100-mark scoring criteria.

---

## 📊 Scoring Category Mapping (Total 100 Marks)

### 1️⃣ Problem Fit & Market Research (25 Marks)
**Judge Expectation:** Correct interpretation, clear use case, focused scope.
**Our Response:**
*   **The Problem:** Industrial downtime costs businesses trillions globally. Unexpected machine failure is a "Trillion Dollar Problem."
*   **The Solution:** PredictAI is an autonomous maintenance agent. It doesn't just "show" data; it predicts failure *before* it happens and takes autonomous action.
*   **Target Market:** CNC Manufacturing, Smart Factories, and Energy Plants.

### 2️⃣ Architecture & Technical Approach (25 Marks)
**Judge Expectation:** Sound data flow, proper module design.
**Our Response:**
*   **Flow:** SSE Stream → `stream_client.py` → **Kafka** (Buffering) → **ML Ensemble** (Brain) → **Decision Engine** (Action) → **Twilio/API** (Outreach) → **Next.js** (Vis).
*   **Highlight:** Mention the use of Kafka for high-frequency data handling—this shows industry-standard scalability.

### 3️⃣ Data Strategy & Realism (20 Marks)
**Judge Expectation:** Noise handling, edge cases, multi-layer reasoning.
**Our Response:**
*   **Preprocessing:** Handles noisy sensor data via Z-Score normalization.
*   **Context:** Uses a 7-day historical dataset to build "per-machine" behavioral baselines.
*   **Logic:** Multi-layered reasoning (Statistical + Unsupervised + Supervised).

### 4️⃣ Feasibility of Detection Logic (20 Marks)
**Judge Expectation:** Specific, mathematically defensible logic.
**Our Response:**
*   **Ensemble Formula:** 
    $$Risk = (0.4 \times XGBoost) + (0.3 \times IsolationForest) + (0.3 \times ZScore)$$
*   **Action Thresholds:**
    *   **Risk < 0.5**: Healthy monitoring.
    *   **0.5 – 0.8**: Proactive SMS Alert.
    *   **> 0.8**: Critical Voice Call + Maintenance Webhook.

### 5️⃣ Team Execution Readiness (10 Marks)
**Judge Expectation:** Visible progress and clear roles.
**Our Response:**
*   **Progress:** Full pipeline is functional. Models are trained. Dashboard is live. Alerting API is connected.
*   **Structure:**
    *   **Member 1**: Data Pipeline & Kafka Orchestration.
    *   **Member 2**: ML Intelligence & Ensemble Design.
    *   **Member 3**: Dashboard & Real-time Visualization.
    *   **Member 4**: Automated Alerts & API Integrations.

---

## 🎤 The 2-Minute Mentor Pitch (Script)

*"Hello. We are Team **beyondminus**, and we’ve built **PredictAI**—an autonomous predictive maintenance agent designed to eliminate industrial downtime.*

*Our system solves a critical gap in manufacturing: **most downtime is preventable if caught minutes before failure.** We don't just alert users; we have built a **closed-loop autonomous system**.*

*Here is how it works:*
1.  *We ingest live sensor telemetry through a **Kafka-powered pipeline** to ensure we can handle thousands of readings per second.*
2.  *Our 'Brain' is a **Multi-Model Ensemble**. We combine **XGBoost** for known failure patterns, **Isolation Forest** for unknown anomalies, and **Dynamic Z-Scores** to understand each machine's unique baseline.*
3.  *The **Decision Engine** then calculates a weighted risk score. If it detects a critical failure path (Risk > 0.8), it doesn't wait for a human. It automatically schedules maintenance via API and initiates a **Voice Call** to the lead engineer using AI-synthesized speech.*

*Every alert, decision, and risk score is visible in real-time on our **Next.js Command Center**. We aren't just predicting the future; we're automating the response to it. Our pipeline is fully functional and ready for the live stream."*

---

## 🏆 Checklist for Round 1
- [x] **Show the Flow Diagram**: Ensure the Mermaid diagram in `PROJECT_FULL_CODE.md` is visible.
- [x] **Demo the Dashboard**: Show the machines in 'Normal' state vs 'Anomaly' state.
- [x] **Trigger an Alert**: Use the "Inject Anomaly" button to show the SMS/Voice trigger logic.
- [x] **Mention 'Kafka' and 'Ensemble'**: These are keywords that mentors value.
