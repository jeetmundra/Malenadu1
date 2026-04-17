CREATE TABLE machines (
    machine_id      VARCHAR(10) PRIMARY KEY,
    name            VARCHAR(100),
    location        VARCHAR(100),
    machine_type    VARCHAR(50),
    status          VARCHAR(20) DEFAULT 'HEALTHY',
    last_seen       TIMESTAMP
);

CREATE TABLE sensor_data (
    id              SERIAL PRIMARY KEY,
    machine_id      VARCHAR(10) REFERENCES machines(machine_id),
    timestamp       BIGINT NOT NULL,
    temperature     FLOAT,
    vibration       FLOAT,
    rpm             INT,
    current         FLOAT,
    pressure        FLOAT,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alerts (
    alert_id        SERIAL PRIMARY KEY,
    machine_id      VARCHAR(10) REFERENCES machines(machine_id),
    risk_score      FLOAT NOT NULL,
    severity        VARCHAR(20) NOT NULL,
    rf_score        FLOAT,
    iso_score       FLOAT,
    z_score         FLOAT,
    lstm_score      FLOAT,
    reason          TEXT,
    acknowledged    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE incidents (
    incident_id     SERIAL PRIMARY KEY,
    machine_id      VARCHAR(10) REFERENCES machines(machine_id),
    alert_id        INT REFERENCES alerts(alert_id),
    description     TEXT,
    status          VARCHAR(20) DEFAULT 'OPEN',
    assigned_to     VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW(),
    resolved_at     TIMESTAMP
);

CREATE TABLE maintenance_schedule (
    id              SERIAL PRIMARY KEY,
    machine_id      VARCHAR(10) REFERENCES machines(machine_id),
    scheduled_at    TIMESTAMP NOT NULL,
    urgency         VARCHAR(20),
    reason          TEXT,
    completed       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE calls (
    call_id         SERIAL PRIMARY KEY,
    machine_id      VARCHAR(10),
    twilio_sid      VARCHAR(100),
    status          VARCHAR(20),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_sensor_machine ON sensor_data(machine_id, timestamp DESC);
CREATE INDEX idx_alerts_machine ON alerts(machine_id, created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity);
