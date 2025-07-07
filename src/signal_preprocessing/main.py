

# main.py

import numpy as np
import pandas as pd
from ecg_signal.ecg_sqa import ECG_SQA  

from pcg_signal.pcg_sqa import PCG_SQA




def load_signals(signal_path, default_fs=500):
    """
    Load ECG and/or PCG signals from a CSV file.

    Args:
        signal_path (str): Path to the signal CSV file.
        default_fs (int): Sampling frequency to use if not provided in file.

    Returns:
        Tuple: (ecg, pcg, fs)
            ecg: np.array or None
            pcg: np.array or None
            fs: int
    """
    df = pd.read_csv(signal_path)
    available_cols = df.columns.str.lower()

    # Detect ECG
    ecg = df['ECG'].values if 'ecg' in available_cols else None

    # Detect PCG
    pcg = df['PCG'].values if 'pcg' in available_cols else None

    # Sampling frequency logic
    if 'fs' in available_cols:
        fs = int(df['fs'].iloc[0])
    else:
        fs = default_fs

    if ecg is None and pcg is None:
        raise ValueError("Neither 'ecg' nor 'pcg' column found in the input file.")

    return ecg, pcg, fs


def run_sqa_analysis(ecg, pcg, fs):
    """
    Runs both ECG and PCG SQA analysis and prints result.
    """
    if ecg is not None:
        # print("\n--- Running ECG Signal Quality Assessment ---")
        ecg_analyzer = ECG_SQA(ecg, fs)
        ecg_report = ecg_analyzer.analyze_all()

    #     print("ECG Report:")
    #     print(f"  Baseline Wander Present : {ecg_report['baseline']['bw_present']}")
    #     print(f"  Abrupt BW Detected      : {ecg_report['baseline']['abw_detected']}")
    #     print(f"  Flatline Segments       : {ecg_report['flatline_segments']}")
    #     print(f"  HF Noise Score          : {ecg_report['hf_noise']}")
    # else:
    #     print("\n--- ECG signal not available, skipping ECG SQA analysis. ---")

    if pcg is not None:
        # print("\n--- Running PCG Signal Quality Assessment ---")
        pcg_analyzer = PCG_SQA(pcg, fs)
        pcg_report = pcg_analyzer.analyze_all()

    #     print("PCG Report:")
    #     print(f"  Flatline Segments       : {pcg_report['flatline_segments']}")
    #     print(f"  HF Noise Score          : {pcg_report['hf_noise']}")
    #     print(f"  Clipping Detected       : {pcg_report['clipping_detected']}")
    #     print(f"  Estimated SNR (dB)      : {pcg_report['snr_db']:.2f} dB")
    # else:
    #     print("\n--- PCG signal not available, skipping PCG SQA analysis. ---")


if __name__ == "__main__":
    ecg, pcg, fs = load_signals(r"C:\Users\abusu\Downloads\1_10-26-08_more_flatlined.csv")
    run_sqa_analysis(ecg, pcg, 1000)
  
    