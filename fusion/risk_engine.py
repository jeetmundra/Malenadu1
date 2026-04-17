import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.isolation_forest import score_iso
from models.xgboost_model import score_rf
from models.stat_engine import score_zscore
from models.lstm_autoencoder import score_lstm
import numpy as np

# Weights must sum to 1.0
WEIGHTS = {
    "rf":   0.40,
    "iso":  0.30,
    "z":    0.20,
    "lstm": 0.10
}

def compute_risk_score(features: dict, machine_id: str, reading: dict,
                       sequence: np.ndarray = None) -> dict:
    # Build feature array in correct order (just dumping values for now)
    # Ensure it's purely numeric for the models
    numeric_features = [v for k,v in features.items() if isinstance(v, (int, float))]
    
    if len(numeric_features) > 0:
        x = np.array(numeric_features)
        rf_score   = score_rf(machine_id, x)
        iso_score  = score_iso(machine_id, x)
    else:
        rf_score = 0.0
        iso_score = 0.0
        
    z_score    = score_zscore(machine_id, reading, features)
    lstm_score = score_lstm(machine_id, sequence) if sequence is not None else 0.0

    risk = (
        WEIGHTS["rf"]   * rf_score  +
        WEIGHTS["iso"]  * iso_score +
        WEIGHTS["z"]    * z_score   +
        WEIGHTS["lstm"] * lstm_score
    )

    return {
        "risk_score":   round(risk, 4),
        "rf_score":     round(rf_score, 4),
        "iso_score":    round(iso_score, 4),
        "z_score":      round(z_score, 4),
        "lstm_score":   round(lstm_score, 4),
        "severity":     classify_severity(risk)
    }

def classify_severity(score: float) -> str:
    if score < 0.30:
        return "LOW"
    elif score < 0.60:
        return "MEDIUM"
    elif score < 0.80:
        return "HIGH"
    else:
        return "CRITICAL"
