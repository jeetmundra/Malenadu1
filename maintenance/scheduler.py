from datetime import datetime, timedelta
import logging

# We import the db directly. If it fails, we catch it.
try:
    from database.db import SessionLocal
    from database.models import MaintenanceSchedule
    HAVE_DB = True
except Exception:
    HAVE_DB = False

logger = logging.getLogger(__name__)

URGENCY_MAP = {
    0:   "IMMEDIATE",
    12:  "URGENT",
    48:  "SCHEDULED",
    168: "ROUTINE"
}

def schedule_maintenance(machine_id: str, hours: int):
    scheduled_at = datetime.utcnow() + timedelta(hours=hours)
    urgency = URGENCY_MAP.get(hours, "SCHEDULED")

    logger.info(f"Scheduling maintenance for {machine_id} at {scheduled_at} ({urgency})")

    if HAVE_DB:
        try:
            db_session = SessionLocal()
            record = MaintenanceSchedule(
                machine_id=machine_id,
                scheduled_at=scheduled_at,
                urgency=urgency,
                reason=f"Auto-scheduled by predictive maintenance agent"
            )
            db_session.add(record)
            db_session.commit()
            db_session.close()
        except Exception as e:
            logger.error(f"Failed to save maintenance schedule to DB: {e}")

    return {"scheduled_at": scheduled_at.isoformat(), "urgency": urgency}
