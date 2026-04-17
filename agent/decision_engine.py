import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import logging

try:
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0)
except Exception:
    r = None

from alerts.sms_service import send_sms
from alerts.voice_service import trigger_voice_call
from maintenance.scheduler import schedule_maintenance
from database.db import SessionLocal
from database.models import Alert, Incident
import requests
from dotenv import load_dotenv

load_dotenv()
HACKATHON_API_URL = os.getenv("HACKATHON_API_URL", "http://localhost:3000")

logger = logging.getLogger(__name__)
COOLDOWN_SECONDS = 300  # 5 min cooldown per machine to prevent alert storms

def push_hackathon_alert(machine_id: str, risk: dict, reading: dict):
    try:
        url = f"{HACKATHON_API_URL}/alert"
        # The official server expects {"machine_id", "reason", "reading"}
        payload = {
            "machine_id": machine_id,
            "reason": risk.get("reason", "Anomaly detected by AI agent"),
            "reading": reading
        }
        res = requests.post(url, json=payload, timeout=5)
        if res.status_code == 201:
            logger.info(f"🚀 Successfully posted alert to Hackathon server for {machine_id}")
        else:
            logger.warning(f"⚠️ Hackathon server rejected alert ({res.status_code})")
    except Exception as e:
        logger.error(f"Failed to post to Hackathon /alert: {e}")

def push_hackathon_maintenance(machine_id: str):
    try:
        url = f"{HACKATHON_API_URL}/schedule-maintenance"
        # The official server supports {"machine_id", "proposed_slot"}
        payload = {
            "machine_id": machine_id,
        }
        res = requests.post(url, json=payload, timeout=5)
        if res.status_code == 201:
            logger.info(f"🔧 Successfully scheduled maintenance on Hackathon server for {machine_id}")
    except Exception as e:
        logger.error(f"Failed to post to Hackathon /schedule-maintenance: {e}")

def decide_action(machine_id: str, risk: dict, reading: dict):
    severity  = risk.get("severity", "LOW")
    score     = risk.get("risk_score", 0.0)
    reason    = risk.get("reason", "")
    cooldown_key = f"cooldown:{machine_id}"

    # 1. Store Alert in Database
    db = SessionLocal()
    new_alert = None
    try:
        new_alert = Alert(
            machine_id=machine_id,
            risk_score=score,
            severity=severity,
            rf_score=risk.get("rf_score"),
            iso_score=risk.get("iso_score"),
            z_score=risk.get("z_score"),
            lstm_score=risk.get("lstm_score"),
            reason=reason
        )
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)
        logger.info(f"[DB LOG] Event logged for {machine_id} - Risk: {score} ({severity})")
    except Exception as e:
        logger.error(f"Failed to save alert to DB: {e}")
        db.rollback()

    # Hackathon bonus: trigger maintenance schedule automatically if risk > 0.8
    triggered_maintenance = False
    if score > 0.8:
        push_hackathon_maintenance(machine_id)
        schedule_maintenance(machine_id, hours=12)
        triggered_maintenance = True

    # Check cooldown (prevent alert storms)
    if r:
        try:
            if r.exists(cooldown_key) and severity in ["MEDIUM", "HIGH", "CRITICAL"]:
                logger.info(f"Machine {machine_id} in cooldown. Skipping escalation.")
                db.close()
                return
        except Exception:
            pass # Redis might be down, ignore cooldown

    if severity == "LOW":
        db.close()
        return

    elif severity == "MEDIUM":
        logger.info(f"[DASHBOARD] Pushing MEDIUM alert for {machine_id}")
        if r:
            try: r.setex(cooldown_key, COOLDOWN_SECONDS, 1)
            except Exception: pass

    elif severity == "HIGH":
        logger.info(f"[DASHBOARD] Pushing HIGH alert for {machine_id}")
        send_sms(machine_id, risk)
        push_hackathon_alert(machine_id, risk, reading)
        if not triggered_maintenance:
            schedule_maintenance(machine_id, hours=12)
        if r:
            try: r.setex(cooldown_key, COOLDOWN_SECONDS, 1)
            except Exception: pass

    elif severity == "CRITICAL":
        logger.info(f"[DASHBOARD] Pushing CRITICAL alert for {machine_id}")
        send_sms(machine_id, risk)
        trigger_voice_call(machine_id, risk)
        
        # Create Incident Ticket in DB
        if new_alert:
            try:
                incident = Incident(
                    machine_id=machine_id,
                    alert_id=new_alert.alert_id,
                    description=f"Automated incident for machine {machine_id}. Severity: {severity}. Score: {score}",
                    status="OPEN",
                    assigned_to="AI_AUTO_AGENT"
                )
                db.add(incident)
                db.commit()
                logger.info(f"[DB LOG] Created incident ticket for {machine_id}")
            except Exception as e:
                logger.error(f"Failed to create incident in DB: {e}")
                db.rollback()
        
        schedule_maintenance(machine_id, hours=0)  # Immediate
        push_hackathon_alert(machine_id, risk, reading)
        if not triggered_maintenance:
            push_hackathon_maintenance(machine_id)
        if r:
            try: r.setex(cooldown_key, COOLDOWN_SECONDS * 2, 1)
            except Exception: pass
    
    db.close()
