from celery import Celery

# Using redis broker. Switch to in-memory/amqp locally if redis isn't present
app = Celery('maintenance', broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')

@app.task
def async_send_sms(machine_id: str, risk: dict):
    from alerts.sms_service import send_sms
    send_sms(machine_id, risk)

@app.task
def async_trigger_call(machine_id: str, risk: dict):
    from alerts.voice_service import trigger_voice_call
    trigger_voice_call(machine_id, risk)

# @app.task
# def async_create_ticket(machine_id: str, risk: dict):
#     from database.db import create_incident_ticket
#     create_incident_ticket(machine_id, risk)
