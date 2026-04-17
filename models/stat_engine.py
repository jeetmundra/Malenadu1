import numpy as np
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.baseline_builder import get_baseline

def score_zscore(machine_id: str, reading: dict, features: dict = None) -> float:
    """
    Returns max z-score across all sensors, scaled 0–1, but uses
    machine-aware custom detection rules if applicable.
    """
    if features is None:
        features = {}

    baseline = get_baseline(machine_id)
    
    # Machine-aware logic overrides generic thresholding
    if machine_id == "CNC_01":
        # Detect: temperature ↑ gradually + vibration ↑ gradually
        temp_slope = features.get("temperature_C_slope", 0)
        vib_slope = features.get("vibration_mm_s_slope", 0)
        if temp_slope > 0.05 and vib_slope > 0.01:
            return 0.8  # HIGH
        
    elif machine_id == "CNC_02":
        # Detect: afternoon temperature spikes
        current_hour = datetime.now().hour
        # Assuming afternoon is 12:00 to 18:00
        if 12 <= current_hour <= 18:
            temp = reading.get("temperature_C", 0)
            temp_mean = baseline.get("temp_mean", temp)
            if temp_mean > 0 and temp > temp_mean * 1.3:
                return 0.9  # CRITICAL
                
    elif machine_id == "PUMP_03":
        # Detect: RPM decreasing trend + vibration bursts
        rpm_slope = features.get("rpm_slope", 0)
        vib = reading.get("vibration_mm_s", 0)
        vib_mean = baseline.get("vib_mean", vib)
        if rpm_slope < -0.5 and vib_mean > 0 and vib > vib_mean * 1.5:
            return 0.85 # HIGH
            
    elif machine_id == "CONVEYOR_04":
        # Treat as baseline reference machine - minimal risk
        return 0.0

    # Generic fallback
    max_z = 0.0
    for col in ["temperature_C", "vibration_mm_s", "rpm", "current_A"]:
        if col not in reading:
            continue
            
        # mapping back to baseline names
        mean_key = "temp_mean" if col == "temperature_C" else "vib_mean" if col == "vibration_mm_s" else f"{col}_mean"
        std_key = "temp_std" if col == "temperature_C" else "vib_std" if col == "vibration_mm_s" else f"{col}_std"
        
        mean = baseline.get(mean_key, reading[col])
        std  = baseline.get(std_key, 1.0)
        if std == 0:
            std = 1.0
            
        z = abs((reading[col] - mean) / (std + 1e-6))
        max_z = max(max_z, z)

    return min(max_z / 5.0, 1.0)
