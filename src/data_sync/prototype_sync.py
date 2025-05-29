import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

def load_signal(file_path, time_col=0, signal_col=1, time_unit='ms'):
    """Load a signal file and extract time and signal arrays."""
    data = pd.read_csv(file_path, header=None).iloc[1:].astype(float)
    time = data.iloc[:, time_col].values
    if time_unit == 'ms':
        time = time / 1000  # Convert ms to s
    signal = data.iloc[:, signal_col].values
    return time, signal

def interpolate_to_common_time(time, signal, t_common):
    """Interpolate a signal to a common timeline."""
    return interp1d(time, signal, kind='linear', fill_value='extrapolate')(t_common)

def synchronize_signals(signals, fs_common=1000):
    """Synchronize multiple signals using interpolation."""
    start_time = max(sig[0][0] for sig in signals)
    end_time = min(sig[0][-1] for sig in signals)
    t_common = np.arange(start_time, end_time, 1/fs_common)

    synced_signals = [interpolate_to_common_time(t, s, t_common) for t, s in signals]
    return t_common, synced_signals

def plot_signals(t_common, signals, labels):
    """Plot synchronized signals."""
    plt.figure(figsize=(14, 6))
    for signal, label in zip(signals, labels):
        plt.plot(t_common, signal, label=label, alpha=0.8)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Synchronized Signals')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# === Load all signals ===
# ecg_time, ecg_signal = load_signal(r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Rel_Data\1_10-09-54_ecg.csv", time_col=0, signal_col=1)
# pcg_time, pcg_signal = load_signal(r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Rel_Data\1_10-09-54_pcg.csv", time_col=0, signal_col=1)
# acc_time, acc_signal = load_signal(r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Rel_Data\1_10-09-54_acc.csv", time_col=0, signal_col=1)

# # === Synchronize signals ===
# t_common, synced_signals = synchronize_signals([
#     (ecg_time, ecg_signal),
#     (pcg_time, pcg_signal),
#     (acc_time, acc_signal)
# ], fs_common=1000)

# # === Plot results ===
# plot_signals(t_common, synced_signals, labels=['ECG (lead I)', 'PCG', 'Accelerometer Az'])



# import os

# # Stack signals into matrix (shape: [n_samples, n_signals])
# synced_matrix = np.vstack(synced_signals).T  # Transpose to get shape (samples, channels)

# # Create DataFrame with column names
# df = pd.DataFrame(synced_matrix, columns=['ECG_lead_I', 'PCG', 'ACC_Z'])
# df['Time'] = t_common

# # Reorder columns so Time is first
# df = df[['Time', 'ECG_lead_I', 'PCG', 'ACC_Z']]

# # Set save path (can modify as needed)
# save_path = r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Rel_Data\synced_signals.csv"
# df.to_csv(save_path, index=False)

# print(f"Synchronized signals saved to:\n{save_path}")