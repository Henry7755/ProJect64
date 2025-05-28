import numpy as np

def generate_timestamps_for_batches(ecg_batches, sampling_rate):
    """
    Generate timestamps for multiple batches of ECG signals.

    Parameters:
    - ecg_batches: List of 1D NumPy arrays, each representing an ECG segment
    - sampling_rate: Sampling rate in Hz

    Returns:
    - List of NumPy arrays containing timestamps (in seconds) for each batch
    """
    if sampling_rate <= 0:
        raise ValueError("Sampling rate must be a positive number.")
    
    timestamps_list = []
    
    for batch in ecg_batches:
        if not isinstance(batch, np.ndarray):
            raise TypeError("Each batch must be a NumPy array.")
        n_samples = len(batch)
        timestamps = np.arange(n_samples) / sampling_rate
        timestamps_list.append(timestamps)
    
    return timestamps_list