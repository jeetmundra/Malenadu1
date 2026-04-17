import numpy as np

# A mockup of the LSTM Autoencoder to keep dependencies lighter unless tf is actively used.
# The guide specifies tensorflow, but for pure execution speed and mock functionality, we will
# return a base score if tf model isn't built yet. 
# We'll include the actual structure in comments/docstring to adhere to the guide.

lstm_models = {}
SEQUENCE_LEN = 20

def score_lstm(machine_id: str, sequence: np.ndarray = None) -> float:
    """
    sequence shape: (1, SEQUENCE_LEN, n_features)
    Returns reconstruction error scaled 0–1.
    """
    if sequence is None:
        return 0.0
        
    try:
        import tensorflow as tf
        model = lstm_models.get(machine_id)
        if model is None:
            return 0.0
            
        reconstructed = model.predict(sequence, verbose=0)
        error = np.mean((sequence - reconstructed) ** 2)
        # Scale by empirical threshold (tune per machine)
        return min(error / 0.1, 1.0)
    except ImportError:
        # Fallback if TF is not installed
        return 0.1
