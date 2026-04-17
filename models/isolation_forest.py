from sklearn.ensemble import IsolationForest
import numpy as np

iso_models = {}

def train_iso(machine_id: str, X_train: np.ndarray):
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,  # Expect ~5% anomalies
        random_state=42
    )
    model.fit(X_train)
    iso_models[machine_id] = model

def score_iso(machine_id: str, x: np.ndarray) -> float:
    """Returns 0 (normal) to 1 (anomaly)"""
    model = iso_models.get(machine_id)
    if model is None:
        return 0.0
    
    # IsolationForest returns -1 for anomaly, +1 for normal
    # We want to return a probabilty/score 0-1 for risk. We can use decision_function
    # instead of direct predict since distance from hyperplane is continuous.
    
    pred = model.predict(x.reshape(1, -1))
    return 1.0 if pred[0] == -1 else 0.0
