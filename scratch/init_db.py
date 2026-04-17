import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database.db import engine, Base
from database.models import Machine, SensorData, Alert, Incident, MaintenanceSchedule, Call

print("Dropping old tables (clean slate)...")
# Drop in correct order due to FK constraints
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS incidents CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS calls CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS maintenance_schedule CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS alerts CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS sensor_data CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS machines CASCADE;"))
    conn.commit()
print("Old tables dropped.")

print("Creating fresh schema...")
Base.metadata.create_all(bind=engine)
print("Schema created successfully.")

# Seed the 4 official machines
from database.db import SessionLocal
db = SessionLocal()
machines = [
    {"machine_id": "CNC_01",      "name": "CNC Mill - 01",        "machine_type": "MILL"},
    {"machine_id": "CNC_02",      "name": "CNC Lathe - 02",       "machine_type": "LATHE"},
    {"machine_id": "PUMP_03",     "name": "Hydraulic Pump - 03",  "machine_type": "PUMP"},
    {"machine_id": "CONVEYOR_04", "name": "System Conveyor - 04", "machine_type": "CONVEYOR"},
]
for m in machines:
    if not db.query(Machine).filter(Machine.machine_id == m["machine_id"]).first():
        db.add(Machine(**m))
db.commit()
db.close()

print("[OK] Machine registry seeded with 4 official hackathon units.")
print("[OK] Database is ready.")
