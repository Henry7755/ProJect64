'''
Unified Signal Quality Assessment for ECG and PCG Signals
This module provides a unified framework for assessing the quality of ECG and PCG signals.  
It includes methods for detecting flatlines, high-frequency noise, baseline wander, clipping, and estimating SNR.

'''


import numpy as np
from scipy.signal import butter, filtfilt, welch, find_peaks
from itertools import groupby

class UnifiedSignalSQA:
    def __init__(self, signal, fs, signal_type):
        """
        Unified Signal Quality Assessment for ECG or PCG.

        Args:
            signal (np.array): 1D signal data (ECG or PCG)
            fs (int): Sampling frequency in Hz
            signal_type (str): 'ecg' or 'pcg'
        """
        self.signal = signal
        self.fs = fs
        self.N = len(signal)
        self.signal_type = signal_type.lower()

    #########################
    # COMMON FUNCTIONS
    #########################

    def _detect_flatline(self, std_thresh, range_thresh, diff_thresh, peak_height, window_sec=2.0, step_sec=1.0):
        win = int(window_sec * self.fs)
        step = int(step_sec * self.fs)
        segments = []

        for i in range(0, self.N - win + 1, step):
            seg = self.signal[i:i+win]
            std = np.std(seg)
            rng = np.ptp(seg)
            mean_diff = np.mean(np.abs(np.diff(seg)))
            peaks, _ = find_peaks(seg, height=peak_height)

            if std < std_thresh and rng < range_thresh and mean_diff < diff_thresh and len(peaks) == 0:
                t1 = i / self.fs
                t2 = (i + win) / self.fs
                segments.append((t1, t2))
        return segments

    def _compute_hf_noise(self, hf_band, window_sec=5.0, min_ratio=0.1):
        win = int(window_sec * self.fs)
        step = win // 2
        segments = [self.signal[i:i + win] for i in range(0, self.N - win + 1, step)]

        ratios = []
        for seg in segments:
            f, psd = welch(seg, fs=self.fs, nperseg=1024)
            total = np.sum(psd)
            hf = np.sum(psd[(f > hf_band[0]) & (f < hf_band[1])])
            ratios.append(hf / total if total > 0 else 0)

        ratios = np.array(ratios)
        threshold = max(min_ratio, np.percentile(ratios, 80))
        noisy_flags = ratios > threshold
        max_streak = max((sum(1 for _ in g) for k, g in groupby(noisy_flags) if k), default=0)

        return {
            "prob_noisy": np.mean(noisy_flags),
            "avg_hf_ratio": np.mean(ratios[noisy_flags]) if np.any(noisy_flags) else 0,
            "adaptive_threshold": threshold,
            "max_noisy_streak": max_streak
        }

    #########################
    # ECG-SPECIFIC METHODS
    #########################

    def _remove_baseline(self, cutoff=1.0):
        freq = np.fft.fftfreq(self.N, 1 / self.fs)
        X = np.fft.fft(self.signal)
        X[np.abs(freq) < cutoff] = 0
        return np.fft.ifft(X).real

    def _detect_ecg_baseline_wander(self, cutoff=1.0, bw_thresh=0.1, abw_thresh=0.2):
        baseline_removed = self._remove_baseline(cutoff)
        residual = self.signal - baseline_removed
        bw_present = np.max(np.abs(residual)) > bw_thresh

        P = int(0.5 * self.fs)
        Q = int(0.25 * self.fs)
        peaks = [np.max(np.abs(residual[start:start + P]))
                 for start in range(0, self.N - P + 1, Q)]

        diffs = np.diff(peaks)
        abw_detected = np.max(np.abs(diffs)) > abw_thresh
        return {"bw_present": bw_present, "abw_detected": abw_detected}

    #########################
    # PCG-SPECIFIC METHODS
    #########################

    def _detect_pcg_clipping(self, clip_thresh=0.95):
        max_val = np.max(np.abs(self.signal))
        return max_val > clip_thresh

    def _estimate_pcg_snr(self, bandpass=(20, 150)):
        b, a = butter(4, [bandpass[0] / (self.fs / 2), bandpass[1] / (self.fs / 2)], btype='band')
        filtered = filtfilt(b, a, self.signal)
        power_total = np.mean(self.signal ** 2)
        power_band = np.mean(filtered ** 2)
        snr = 10 * np.log10(power_band / (power_total - power_band + 1e-12))
        return snr

    #########################
    # MAIN ANALYSIS ENTRY
    #########################

    def analyze(self):
        if self.signal_type == 'ecg':
            return {
                "signal_type": "ecg",
                "baseline": self._detect_ecg_baseline_wander(),
                "flatline_segments": self._detect_flatline(
                    std_thresh=0.01, range_thresh=0.005,
                    diff_thresh=0.01, peak_height=0.05),
                "hf_noise": self._compute_hf_noise(hf_band=(45, 100))
            }

        elif self.signal_type == 'pcg':
            return {
                "signal_type": "pcg",
                "flatline_segments": self._detect_flatline(
                    std_thresh=0.01, range_thresh=0.005,
                    diff_thresh=0.001, peak_height=0.05),
                "hf_noise": self._compute_hf_noise(hf_band=(500, 1500)),
                "clipping_detected": self._detect_pcg_clipping(),
                "snr_db": self._estimate_pcg_snr()
            }

        else:
            raise ValueError(f"Unsupported signal type: {self.signal_type}")
