from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json
import os
import sys
import redis
import logging
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from maintenance.scheduler import schedule_maintenance
from database.db import get_db
from database.models import Alert, Incident
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

app = FastAPI(title="Predictive Maintenance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for inter-process communication
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

OFFICIAL_MACHINES = ["CNC_01", "CNC_02", "PUMP_03", "CONVEYOR_04"]

def get_latest_reading(machine_id: str):
    try:
        data = r.get(f"latest_status:{machine_id}")
        if data:
            return json.loads(data)
    except Exception as e:
        logger.error(f"Redis error: {e}")
    return {"status": "Waiting for stream..."}

@app.get("/stream/{machine_id}")
async def stream_sensor(machine_id: str):
    """Server-Sent Events — live sensor readings enriched with AI risk"""
    async def event_gen():
        while True:
            data = get_latest_reading(machine_id)
            if data and data.get("status") != "Waiting for stream...":
                yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1) # Stream at 1Hz
            
    return StreamingResponse(event_gen(), media_type="text/event-stream")

@app.get("/machine-status")
def all_machine_status():
    status = {}
    for m in OFFICIAL_MACHINES:
        data = get_latest_reading(m)
        status[m] = data
    return status

@app.get("/alerts")
def list_alerts(machine_id: str = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Alert)
    if machine_id:
        query = query.filter(Alert.machine_id == machine_id)
    return query.order_by(Alert.created_at.desc()).limit(limit).all()

@app.get("/incidents")
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).filter(Incident.status == "OPEN").all()

@app.post("/schedule-maintenance")
def schedule(payload: dict):
    # This matches the dashboard's maintenance trigger
    return schedule_maintenance(payload.get("machine_id"), payload.get("hours", 0))

@app.get("/risk/{machine_id}")
def current_risk(machine_id: str):
    data = get_latest_reading(machine_id)
    return data.get("risk", {})

@app.post("/inject-anomaly/{machine_id}")
def inject_anomaly(machine_id: str):
    # This feeds back to the simulator if needed
    r.setex(f"anomaly_trigger:{machine_id}", 10, "1")
    return {"status": "Anomaly triggered", "machine_id": machine_id}
