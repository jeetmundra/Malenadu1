import random
import time
import json
import logging
import os
import redis
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis for inter-process communication
r = redis.Redis(host='localhost', port=6379, db=0)

# Fallback for when Kafka isn't running yet during local dev testing
try:
    producer = KafkaProducer(
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    logger.info("Connected to Kafka.")
except Exception as e:
    logger.warning(f"Failed to connect to Kafka. Creating a mock producer. {e}")
    class MockProducer:
        def send(self, topic, value):
            logger.debug(f"[MOCK KAFKA] -> {topic}: {value}")
    producer = MockProducer()

MACHINES = ["M1", "M2", "M3", "M4"]

def generate_reading(machine_id, inject_anomaly=False):
    base = {
        "machine_id": machine_id,
        "timestamp": int(time.time()),
        "temperature": random.uniform(60, 80),
        "vibration": random.uniform(0.2, 0.5),
        "rpm": random.randint(1400, 1600),
        "current": random.uniform(4.5, 6.5),
        "pressure": random.uniform(2.5, 3.5)
    }
    
    if inject_anomaly:
        logger.warning(f"Injecting anomaly for {machine_id}")
        base["temperature"] = random.uniform(88, 95)   # spike
        base["vibration"] = random.uniform(0.8, 1.2)   # spike
        base["rpm"] = random.randint(1200, 1300)       # drop
        base["current"] = random.uniform(7.5, 9.0)     # spike
        
    return base

if __name__ == "__main__":
    logger.info("Starting Sensor Simulator...")
    while True:
        for m in MACHINES:
            # 1. Check Redis for manual anomaly trigger (10 second window)
            redis_trigger = r.exists(f"anomaly_trigger:{m}")
            
            # 2. Occasional random anomaly in M2 (original logic)
            random_trigger = (m == "M2" and random.random() < 0.05)
            
            anomaly = redis_trigger or random_trigger
            data = generate_reading(m, inject_anomaly=anomaly)
            producer.send("machine_stream", data)
        time.sleep(1)
