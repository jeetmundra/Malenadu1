import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.baseline_builder import get_baseline

buffers = {m: [] for m in ["CNC_01", "CNC_02", "PUMP_03", "CONVEYOR_04"]}

def compute_features(reading: dict) -> dict:
    mid = reading.get("machine_id", "CNC_01")
    buf = buffers.get(mid, [])
    
    buf.append(reading)
    if len(buf) > 50:
        buf.pop(0)
    
    buffers[mid] = buf
    df = pd.DataFrame(buf)
    baseline = get_baseline(mid)
    features = {}

    for col in ["temperature_C", "vibration_mm_s", "rpm", "current_A"]:
        if col not in reading:
            continue
            
        val = reading[col]
        # mapping to baseline names
        mean_key = "temp_mean" if col == "temperature_C" else "vib_mean" if col == "vibration_mm_s" else f"{col}_mean"
        std_key = "temp_std" if col == "temperature_C" else "vib_std" if col == "vibration_mm_s" else f"{col}_std"
        
        mean = baseline.get(mean_key, val)
        std  = baseline.get(std_key, 1.0)
        
        if std == 0:
            std = 1.0

        features[f"{col}_roll_mean_5"]  = df[col].rolling(min(5, len(df))).mean().iloc[-1]
        features[f"{col}_roll_std_5"]   = df[col].rolling(min(5, len(df))).std().iloc[-1] if len(df) >= 2 else 0.0
        features[f"{col}_roll_mean_20"] = df[col].rolling(min(20, len(df))).mean().iloc[-1]

        features[f"{col}_lag1"] = df[col].shift(1).iloc[-1] if len(df) > 1 else val
        features[f"{col}_lag2"] = df[col].shift(2).iloc[-1] if len(df) > 2 else val

        features[f"{col}_diff"] = df[col].diff().iloc[-1] if len(df) > 1 else 0

        features[f"{col}_zscore"] = (val - mean) / (std + 1e-6)

        if len(df) >= 10:
            y = df[col].iloc[-10:].values
            x = np.arange(10)
            slope = np.polyfit(x, y, 1)[0]
            features[f"{col}_slope"] = slope
        else:
            features[f"{col}_slope"] = 0

    return features
