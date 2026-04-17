@echo off
echo Starting FastAPI Backend...
start cmd /k "venv\Scripts\activate && uvicorn api.main:app --reload --port 8000"

echo Starting Kafka Consumer (ML Pipeline)...
start cmd /k "venv\Scripts\activate && python consumer/kafka_consumer.py"

echo Starting Celery Worker...
start cmd /k "venv\Scripts\activate && celery -A celery_app worker --loglevel=info"

echo Starting Sensor Simulator...
start cmd /k "venv\Scripts\activate && python producer/sensor_simulator.py"

echo All backend services started in separate windows!
