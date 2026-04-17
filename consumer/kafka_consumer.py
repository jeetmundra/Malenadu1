import json
import logging
import time
import os
import sys
import redis

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaConsumer
from features.feature_engineering import compute_features
from fusion.risk_engine import compute_risk_score
from agent.decision_engine import decide_action
from agent.explainer import generate_explanation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis for inter-process communication
r = redis.Redis(host='localhost', port=6379, db=0)

def start_consumer():
    try:
        consumer = KafkaConsumer(
            "sensor_readings",
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        logger.info("Listening to Kafka Topic: sensor_readings")

        for message in consumer:
            reading = message.value
            machine_id = reading["machine_id"]
            
            # 1. Feature Engineering
            features = compute_features(reading)
            
            # 2. ML Engine (Scoring)
            risk = compute_risk_score(features, machine_id, reading)
            
            # 3. Agentic Explanation Engine
            generate_explanation(machine_id, reading, features, risk)
            
            # Update Redis state for the API
            r.set(f"latest_status:{machine_id}", json.dumps({
                "reading": reading,
                "risk": risk
            }))
            
            # 4. Agentic Decision Engine (Act/Escalate)
            decide_action(machine_id, risk, reading)
            
    except Exception as e:
        logger.warning(f"Kafka consumer failed to start. {e}")

if __name__ == "__main__":
    start_consumer()
