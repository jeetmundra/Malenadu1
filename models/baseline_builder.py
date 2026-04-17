import numpy as np
import pandas as pd
import json
import os

BASELINE_FILE = os.path.join(os.path.dirname(__file__), "baselines.json")

baselines = {}

def load_baselines():
    global baselines
    if os.path.exists(BASELINE_FILE):
        try:
            with open(BASELINE_FILE, "r") as f:
                baselines = json.load(f)
        except Exception:
            pass

def save_baselines():
    with open(BASELINE_FILE, "w") as f:
        json.dump(baselines, f, indent=4)

load_baselines()

def build_baseline(machine_id: str, df: pd.DataFrame):
    baseline = {}
    
    # Safely get means depending on what's available
    if "temperature_C" in df.columns:
        baseline["temp_mean"] = df["temperature_C"].mean()
        baseline["temp_std"] = df["temperature_C"].std() if len(df) > 1 else 1.0
    if "vibration_mm_s" in df.columns:
        baseline["vib_mean"] = df["vibration_mm_s"].mean()
        baseline["vib_std"] = df["vibration_mm_s"].std() if len(df) > 1 else 1.0
    if "rpm" in df.columns:
        baseline["rpm_mean"] = df["rpm"].mean()
        baseline["rpm_std"] = df["rpm"].std() if len(df) > 1 else 1.0
    if "current_A" in df.columns:
        baseline["current_mean"] = df["current_A"].mean()
        baseline["current_std"] = df["current_A"].std() if len(df) > 1 else 1.0

    baselines[machine_id] = baseline
    save_baselines()
    return baseline

def get_baseline(machine_id: str):
    return baselines.get(machine_id, {})
