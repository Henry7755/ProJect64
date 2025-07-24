from sklearn.base import BaseEstimator, TransformerMixin
import scipy.signal as sig
import yaml
import numpy as np

class PCGfilter(BaseEstimator, TransformerMixin):
    """SQA-aware PCG filtering pipeline."""
    def __init__(self, fs, lowcut=20, highcut=400, order=4, config_path=None, sqa_result=None):
        self.fs = fs
        self.lowcut = lowcut
        self.highcut = highcut
        self.order = order
        self.config_path = config_path
        self.sqa_result = sqa_result

        if self.config_path:
            try:
                with open(self.config_path, 'r') as file:
                    self.config = yaml.safe_load(file)
            except Exception as e:
                print(f"Error loading config file: {e}")
                self.config = {}
        else:
            print("Config path not provided. Using default parameters.")
            self.config = {
                "pcg_filter_config": {
                    "snr_threshold": 5.0,
                    "hf_noise_threshold": 0.4,
                    "clipping_threshold": 0.95
                }
            }

    def set_sqa_result(self, sqa_result, sqa_mask=None):
        """Setter to inject SQA results."""
        self.sqa_result = sqa_result
        self.sqa_mask = sqa_mask

    def bandpass(self, signal, filter_type='butter'):
        nyquist = 0.5 * self.fs
        low = self.lowcut / nyquist
        high = self.highcut / nyquist
        sos = sig.butter(self.order, [low, high], btype='bandpass', output='sos')
        return sig.sosfiltfilt(sos, signal)

    def clip_protection(self, signal):
        """Apply simple clipping protection by soft normalization."""
        max_val = np.max(np.abs(signal))
        if max_val > 1.0:
            signal = signal / max_val
        return signal

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """
        Apply filtering conditionally based on SQA findings.
        """
        if self.sqa_result is None:
            raise ValueError("SQA result not set. Use `.set_sqa_result()` or pass in constructor.")

        snr_thresh = self.config["pcg_filter_config"].get("snr_threshold", 5.0)
        hf_noise_thresh = self.config["pcg_filter_config"].get("hf_noise_threshold", 0.4)

        # STEP 1: Skip or flag flatlines
        flat_segs = self.sqa_result.get("flatline_segments", [])
        if len(flat_segs) > 0:
            print("Warning: Flatline segments detected. Consider masking these regions.")
            # Optional: replace flatline regions or mark them

        # STEP 2: Clipping check
        if self.sqa_result.get("clipping_detected", False):
            print("Warning: Amplitude clipping detected. Applying normalization.")
            X = self.clip_protection(X)

        # STEP 3: Apply bandpass filtering only if SNR is low or HF noise is high
        snr_db = self.sqa_result.get("snr_db", 10.0)
        prob_noisy = self.sqa_result.get("hf_noise", {}).get("prob_noisy", 0.0)

        if snr_db < snr_thresh or prob_noisy > hf_noise_thresh:
            X = self.bandpass(X)
        else:
            print("PCG signal quality good — skipping aggressive filtering.")

        return X
