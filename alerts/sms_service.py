import os
import logging
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def send_sms(machine_id: str, risk: dict):
    logger.info(f"Preparing to send SMS for machine {machine_id}")
    try:
        # We only throw actual twilio requests if credentials exist.
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            logger.warning("Twilio keys not found in ENV. Mocking SMS send.")
            logger.info(f"MOCK SMS SENT: Machine {machine_id} - Risk: {risk['risk_score']}")
            return

        client = Client(account_sid, auth_token)
        msg = (
            f"⚠️ MAINTENANCE ALERT\n"
            f"Machine {machine_id} — {risk['severity']}\n"
            f"Risk Score: {risk['risk_score']:.2f}\n"
            f"Action required immediately."
        )
        client.messages.create(
            body=msg,
            from_=os.getenv("TWILIO_FROM"),
            to=os.getenv("ENGINEER_PHONE")
        )
        logger.info(f"SMS successfully sent for machine {machine_id}")
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
