from sqlalchemy import Column, Integer, String, Float, Boolean, BigInteger, DateTime, ForeignKey, Text
from datetime import datetime
from .db import Base

class Machine(Base):
    __tablename__ = "machines"
    machine_id = Column(String(20), primary_key=True)
    name = Column(String(100))
    location = Column(String(100))
    machine_type = Column(String(50))
    status = Column(String(20), default='HEALTHY')
    last_seen = Column(DateTime)

class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(20), ForeignKey("machines.machine_id"), index=True)
    timestamp = Column(BigInteger, nullable=False)
    temperature = Column(Float)
    vibration = Column(Float)
    rpm = Column(Integer)
    current = Column(Float)
    pressure = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    alert_id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(20), ForeignKey("machines.machine_id"), index=True)
    risk_score = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    rf_score = Column(Float)
    iso_score = Column(Float)
    z_score = Column(Float)
    lstm_score = Column(Float)
    reason = Column(Text)
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Incident(Base):
    __tablename__ = "incidents"
    incident_id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(20), ForeignKey("machines.machine_id"))
    alert_id = Column(Integer, ForeignKey("alerts.alert_id"))
    description = Column(Text)
    status = Column(String(20), default='OPEN')
    assigned_to = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedule"
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(20), ForeignKey("machines.machine_id"))
    scheduled_at = Column(DateTime, nullable=False)
    urgency = Column(String(20))
    reason = Column(Text)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Call(Base):
    __tablename__ = "calls"
    call_id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String(20))
    twilio_sid = Column(String(100))
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
