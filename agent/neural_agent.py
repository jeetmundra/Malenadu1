import os
import sys
import json
import time
import logging
import numpy as np
import redis
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.stat_engine import score_zscore
from models.isolation_forest import score_iso
from models.xgboost_model import score_rf
from agent.explainer import generate_explanation
from agent.decision_engine import decide_action
from hackathon_integration.ingest_history import ingest_historical_api

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NeuralAgent")

# Config
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Initialize Redis
try:
    r_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    r_client = None

def start_agent():
    # 1. Warm up: Ingest history & train models
    logger.info("Initializing Agent Brain (Pre-training)...")
    ingest_historical_api()
    
    # 2. Connect to Telemetry Stream
    logger.info(f"Connecting to Kafka at {KAFKA_BROKER}...")
    try:
        consumer = KafkaConsumer(
            'sensor_readings',
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='neural-agent-group',
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        return

    logger.info("Neural Agent is LIVE and listening to telemetry...")

    sensor_cols = ["temperature_C", "vibration_mm_s", "rpm", "current_A"]

    for message in consumer:
        reading = message.value
        machine_id = reading.get("machine_id")
        
        if not machine_id: continue
        
        # Prepare feature vector for ML
        try:
            x = np.array([reading.get(col, 0) for col in sensor_cols]).reshape(1, -1)
            
            # 3. Triple-Check Inference
            z_score   = score_zscore(machine_id, reading)
            iso_score = score_iso(machine_id, x)
            rf_score  = score_rf(machine_id, x)
            
            # Decision weights: 40% XGBoost, 30% IsoForest, 30% Stat Baseline
            risk_score = (0.4 * rf_score) + (0.3 * iso_score) + (0.3 * z_score)
            
            severity = "LOW"
            if risk_score > 0.8:   severity = "CRITICAL"
            elif risk_score > 0.6: severity = "HIGH"
            elif risk_score > 0.3: severity = "MEDIUM"
            
            risk_data = {
                "risk_score": float(risk_score),
                "severity": severity,
                "z_score": float(z_score),
                "iso_score": float(iso_score),
                "rf_score": float(rf_score),
                "reason": "" # Will be populated by explainer
            }
            
            # 4. Generate Explainable AI (XAI) Reason
            generate_explanation(machine_id, reading, {}, risk_data)
            
            # 5. Broadcast Enriched Telemetry to Dashboard (via Redis)
            if r_client:
                dashboard_packet = {
                    "reading": reading,
                    "risk": risk_data
                }
                r_client.set(f"latest_status:{machine_id}", json.dumps(dashboard_packet))
            
            # 6. Execute Autonomous Decision
            decide_action(machine_id, risk_data, reading)
            
            if severity != "LOW":
                logger.warning(f"ALERT [{machine_id}] {severity} (Score: {risk_score:.2f}) - {risk_data['reason']}")
            else:
                logger.info(f"OK [{machine_id}] Health: {1.0-risk_score:.2f}")

        except Exception as e:
            logger.error(f"Error processing reading for {machine_id}: {e}")

if __name__ == "__main__":
    start_agent()
