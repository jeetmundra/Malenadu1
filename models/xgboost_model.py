from xgboost import XGBClassifier
import numpy as np

rf_models = {}

def train_rf(machine_id: str, X_train: np.ndarray, y_train: np.ndarray):
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)
    rf_models[machine_id] = model

def score_rf(machine_id: str, x: np.ndarray) -> float:
    """Returns probability of failure (0 to 1)"""
    model = rf_models.get(machine_id)
    if model is None:
        # Dummy behavior for MVP without training data
        return 0.0
    prob = model.predict_proba(x.reshape(1, -1))[0][1]
    return float(prob)
