#   __--- Normalization ---__
import numpy as np

def normalize_signal(signal):
    """
    Normalize the ECG signal to a range of [0, 1].
    
    Parameters:
    signal (np.ndarray): The ECG signal to normalize.
    
    Returns:
    np.ndarray: The normalized ECG signal.
    """
    if len(signal) == 0:
        raise ValueError("Input signal is empty.")
    
    min_val = np.min(signal)
    max_val = np.max(signal)
    
    if min_val == max_val:
        raise ValueError("Input signal has no variation (min equals max).")
    
    normalized_signal = (signal - min_val) / (max_val - min_val)
    
    return normalized_signal


def z_score_normalize(signal):
    """
    Performs z-score standardization on a signal.

    Args:
        signal (np.ndarray): The input PCG signal.

    Returns:
        np.ndarray: The standardized PCG signal.
    """
    mean_val = np.mean(signal)
    std_val = np.std(signal)

    if std_val == 0:
        standardized_signal = np.zeros_like(signal)
    else:
        standardized_signal = (signal - mean_val) / std_val

    return standardized_signal