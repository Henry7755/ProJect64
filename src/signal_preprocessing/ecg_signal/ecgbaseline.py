import numpy as np

class ECGBaselineAnalyzer:
    def __init__(self, ecg_signal, fs):
        """
        Initialize with ECG signal and sampling frequency.
        """
        self.ecg_signal = ecg_signal
        self.fs = fs
        self.N = len(ecg_signal)
        self.freq = np.fft.fftfreq(self.N, 1 / fs)
        self.baseline_removed = None
        self.bw_present = False
        self.abw_detected = False

    def remove_baseline(self):
        """
        Perform DFT-based baseline removal.
        """
        X = np.fft.fft(self.ecg_signal)
        X_filtered = X.copy()
        X_filtered[np.abs(self.freq) < 1.0] = 0
        self.baseline_removed = np.fft.ifft(X_filtered).real
        return self.baseline_removed

    def detect_bw_and_abw(self):
        """
        Detect baseline wander (BW) and abrupt BW (ABW).
        """
        if self.baseline_removed is None:
            self.remove_baseline()

        b = self.ecg_signal - self.baseline_removed
        Ag = np.max(np.abs(b))
        self.bw_present = Ag > 0.1  # BW threshold in mV

        # Segment signal into blocks
        P = int(0.5 * self.fs)  # 500 ms
        Q = int(0.25 * self.fs)  # 50% overlap
        L = (self.N - P) // Q + 1

        ak = []
        for i in range(L):
            start = i * Q
            block = b[start:start + P]
            if len(block) == P:
                ak.append(np.max(np.abs(block)))

        ak = np.array(ak)
        d = np.diff(ak)
        self.abw_detected = np.max(np.abs(d)) > 0.2  # ABW threshold in mV

        return self.bw_present, self.abw_detected

    def analyze(self):
        """
        Run full analysis pipeline: baseline removal + BW/ABW detection.
        """
        self.remove_baseline()
        return self.detect_bw_and_abw()



# Sample usage
import numpy as np
import pandas as pd


# Simulated ECG with low-frequency drift
fs = 500  # sampling rate in Hz
ecg = pd.read_csv(r'C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Synched_Data\6_11-05-07_synced.csv')['ECG']
# Analyze
analyzer = ECGBaselineAnalyzer(ecg, fs)
bw_present, abw_detected = analyzer.analyze()

print("BW Present:", bw_present)
print("ABW Detected:", abw_detected)
