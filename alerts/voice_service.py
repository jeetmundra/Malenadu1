import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def trigger_voice_call(machine_id: str, risk: dict):
    logger.info(f"Triggering Voice Call for {machine_id}")
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        logger.warning("Twilio / ElevenLabs keys not found. Mocking voice call.")
        reason = risk.get('reason', 'multiple sensor anomalies').replace('\n', ' ')
        script = (
            f"Critical maintenance alert. Machine {machine_id} has a risk score of "
            f"{risk['risk_score']:.2f}. Immediate inspection is required. "
            f"The system has detected {reason}. "
            f"Please acknowledge this alert on the dashboard."
        )
        logger.info(f"[MOCK VOICE SPEECH]: {script}")
        return

    try:
        from twilio.rest import Client
        from elevenlabs import generate, Voice
        
        # In a fully deployed system, we would:
        # 1. generate audio with elevenlabs
        # 2. save to an S3 bucket or equivalent public URl
        # 3. provide URL in twiml response to Twilio
        
        twilio_client = Client(account_sid, auth_token)
        
        # Simplified Twiml for text-to-speech fallback if elevenlabs fails/not connected
        script = f"Critical maintenance alert. Machine {machine_id} has a critical risk score. Immediate inspection required."
        twiml = f'<Response><Say>{script}</Say></Response>'
        
        twilio_client.calls.create(
            twiml=twiml,
            from_=os.getenv("TWILIO_FROM"),
            to=os.getenv("ENGINEER_PHONE")
        )
        logger.info("Outbound call triggered successfully.")
    except Exception as e:
        logger.error(f"Failed to trigger voice call: {e}")
