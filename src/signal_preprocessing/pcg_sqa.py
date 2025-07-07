import numpy as np
from scipy.signal import butter, filtfilt, welch, find_peaks


class PCG_SQA:
    def __init__(self, pcg_signal, fs):
        """
        PCG Signal Quality Assessment.

        Args:
            pcg_signal (np.array): PCG signal (1D)
            fs (int): Sampling frequency in Hz
        """
        self.pcg = pcg_signal
        self.fs = fs
        self.N = len(pcg_signal)

    def detect_flatline(self, window_sec=2.0, step_sec=1.0,
                        std_thresh=0.01, range_thresh=0.005,
                        diff_thresh=0.001, peak_height=0.05):
        """
        Detect flat segments in PCG (e.g., disconnected mic).
        Returns:
            List of (start_time, end_time) in seconds.
        """
        win = int(window_sec * self.fs)
        step = int(step_sec * self.fs)
        segments = []

        for i in range(0, self.N - win + 1, step):
            seg = self.pcg[i:i+win]
            std = np.std(seg)
            rng = np.ptp(seg)
            mean_diff = np.mean(np.abs(np.diff(seg)))
            peaks, _ = find_peaks(seg, height=peak_height)

            if std < std_thresh and rng < range_thresh and mean_diff < diff_thresh and len(peaks) == 0:
                t1 = i / self.fs
                t2 = (i + win) / self.fs
                segments.append((t1, t2))

        return segments

    def detect_high_freq_noise(self, hf_band=(500, 1500), window_sec=5.0, min_ratio=0.1):
        """
        Detect high-frequency noise in PCG (e.g., stethoscope brushing).

        Returns:
            dict: {prob_noisy, avg_hf_ratio, adaptive_threshold, max_noisy_streak}
        """
        win = int(window_sec * self.fs)
        step = win // 2
        segments = [self.pcg[i:i + win] for i in range(0, self.N - win + 1, step)]

        ratios = []
        for seg in segments:
            f, psd = welch(seg, fs=self.fs, nperseg=1024)
            total = np.sum(psd)
            hf = np.sum(psd[(f > hf_band[0]) & (f < hf_band[1])])
            ratios.append(hf / total if total > 0 else 0)

        ratios = np.array(ratios)
        threshold = max(min_ratio, np.percentile(ratios, 80))
        noisy_flags = ratios > threshold

        from itertools import groupby
        max_streak = max((sum(1 for _ in g) for k, g in groupby(noisy_flags) if k), default=0)

        return {
            "prob_noisy": np.mean(noisy_flags),
            "avg_hf_ratio": np.mean(ratios[noisy_flags]) if np.any(noisy_flags) else 0,
            "adaptive_threshold": threshold,
            "max_noisy_streak": max_streak
        }

    def detect_amplitude_clipping(self, clip_thresh=0.95):
        """
        Detects whether the PCG signal is saturating (clipping).
        Returns:
            bool: True if clipping detected
        """
        max_val = np.max(np.abs(self.pcg))
        return max_val > clip_thresh

    def estimate_snr(self, bandpass=(20, 150)):
        """
        Estimate SNR: bandpass energy vs residual.

        Returns:
            float: SNR in decibels (dB)
        """
        b, a = butter(4, [bandpass[0] / (self.fs / 2), bandpass[1] / (self.fs / 2)], btype='band')
        filtered = filtfilt(b, a, self.pcg)
        power_total = np.mean(self.pcg ** 2)
        power_band = np.mean(filtered ** 2)
        snr = 10 * np.log10(power_band / (power_total - power_band + 1e-12))
        return snr

    def analyze_all(self):
        """
        Run full SQA for PCG signal.

        Returns:
            dict: All analysis results.
        """
        return {
            "flatline_segments": self.detect_flatline(),
            "hf_noise": self.detect_high_freq_noise(),
            "clipping_detected": self.detect_amplitude_clipping(),
            "snr_db": self.estimate_snr(),
        }
