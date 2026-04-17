import pandas as pd
import numpy as np
import os
import sys
import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.baseline_builder import build_baseline
from models.isolation_forest import train_iso
from models.xgboost_model import train_rf

load_dotenv()
HACKATHON_API_URL = os.getenv("HACKATHON_API_URL", "http://localhost:3000")

def ingest_historical_api():
    print(f"Initializing Historical Ingestion from {HACKATHON_API_URL}...")
    
    # Machine Registry
    try:
        m_res = requests.get(f"{HACKATHON_API_URL}/machines")
        machines = m_res.json().get("machines", ["CNC_01", "CNC_02", "PUMP_03", "CONVEYOR_04"])
    except:
        machines = ["CNC_01", "CNC_02", "PUMP_03", "CONVEYOR_04"]

    all_dfs = []

    for m in machines:
        print(f"[FETCH] Fetching 7-day archive for {m}...")
        try:
            res = requests.get(f"{HACKATHON_API_URL}/history/{m}", timeout=30)
            if res.status_code == 200:
                data = res.json()
                readings = data.get("readings", [])
                if readings:
                    m_df = pd.DataFrame(readings)
                    # Enforce machine_id if missing in JSON
                    if 'machine_id' not in m_df.columns:
                        m_df['machine_id'] = m
                    all_dfs.append(m_df)
                    print(f"[OK] Loaded {len(readings)} rows for {m}")
            else:
                print(f"[ERR] Server Error ({res.status_code}) for {m}")
        except Exception as e:
            print(f"[WARN] Connection Error for {m}: {e}")

    if not all_dfs:
        print("[CRITICAL] Error: No historical data could be retrieved. Check if the server is running.")
        return

    full_df = pd.concat(all_dfs, ignore_index=True)
    
    for m_id in machines:
        m_df = full_df[full_df['machine_id'] == m_id].copy()
        if m_df.empty: continue

        if "timestamp" in m_df.columns:
            m_df = m_df.sort_values(by="timestamp")

        print(f"\n[MODEL] Calibrating Brain for {m_id}...")
        
        # 1. Build and Save Baseline
        build_baseline(m_id, m_df)
        
        # 2. Train Models
        cols_to_use = ["temperature_C", "vibration_mm_s", "rpm", "current_A"]
        X_train = m_df[cols_to_use].fillna(method='ffill').fillna(0).values
        
        print(f"   - Training Isolation Forest (Unsupervised)...")
        train_iso(m_id, X_train)
        
        # 3. Train XGBoost if failure labels exist
        if "status" in m_df.columns:
            y_train = m_df['status'].apply(lambda x: 1 if str(x).lower() in ["fault", "warning"] else 0).values
            if len(np.unique(y_train)) > 1:
                print(f"   - Training XGBoost (Supervised)...")
                train_rf(m_id, X_train, y_train)
            else:
                print(f"   - Skipping XGBoost: No failure samples in history for {m_id}.")
        
    print("\n[OK] PRE-HACKATHON CALIBRATION COMPLETE.")
    print("The agent is now tuned to the machine behavioral baselines.")

if __name__ == "__main__":
    ingest_historical_api()
