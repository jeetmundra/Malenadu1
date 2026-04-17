import os
import sys
import time
import json
import requests
from kafka import KafkaProducer
from sseclient import SSEClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

HACKATHON_API_URL = os.getenv("HACKATHON_API_URL", "http://localhost:3000")
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def listen_to_stream(machine_id: str):
    url = f"{HACKATHON_API_URL}/stream/{machine_id}"
    print(f"[{machine_id}] Connecting to stream: {url}")
    
    last_received = time.time()
    
    while True:
        try:
            response = requests.get(url, stream=True, timeout=10)
            client = SSEClient(response)
            for event in client.events():
                if event.data:
                    last_received = time.time()
                    try:
                        raw_data = json.loads(event.data)
                        # Pass exactly 4 sensors as required + machine_id
                        producer.send("sensor_readings", raw_data)
                        print(f"[{machine_id}] Data received -> Kafka")
                    except json.JSONDecodeError:
                        print(f"[{machine_id}] Unparseable event data")
        except (requests.exceptions.RequestException, Exception) as e:
            time_since_last = time.time() - last_received
            print(f"[{machine_id}] Stream disconnected ({e}). No data for {int(time_since_last)}s. Reconnecting in 3s...")
            
            if time_since_last > 15:
                signal = {
                    "machine_id": machine_id,
                    "timestamp": int(time.time()),
                    "temperature_C": 0, "vibration_mm_s": 0, "rpm": 0, "current_A": 0,
                    "status": "DATA_ABSENT_SIGNAL"
                }
                producer.send("sensor_readings", signal)
            
            time.sleep(3)

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    
    print("Starting Hackathon Live Stream Client...")
    print(f"Targeting Hackathon Server: {HACKATHON_API_URL}")

    # Machine registry auto-loader (Change 10)
    try:
        machines_res = requests.get(f"{HACKATHON_API_URL}/machines")
        machines = machines_res.json().get("machines", ["CNC_01", "CNC_02", "PUMP_03", "CONVEYOR_04"])
    except Exception as e:
        print(f"Failed to fetch /machines (using default list): {e}")
        machines = ["CNC_01", "CNC_02", "PUMP_03", "CONVEYOR_04"]

    print(f"Connecting to streams for machines: {machines}")
    
    with ThreadPoolExecutor(max_workers=len(machines)) as executor:
        for m in machines:
            executor.submit(listen_to_stream, m)
