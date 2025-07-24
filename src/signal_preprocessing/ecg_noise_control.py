# -*- coding: utf-8 -*-
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import scipy.signal as signal
import yaml

class ECGfilter(BaseEstimator, TransformerMixin):
    """SQA-aware ECG filtering pipeline."""
    def __init__(self, fs=500, lowcut=0.5, highcut=45, order=4,
                 config=None, config_path=None, sqa_result=None):
        self.fs = fs
        self.lowcut = lowcut
        self.highcut = highcut
        self.order = order
        self.config = config or {}
        self.config_path = config_path
        self.sqa_result = sqa_result  # Injected externally

        if self.config_path:
            try:
                with open(self.config_path, 'r') as file:
                    self.config = yaml.safe_load(file)
            except Exception as e:
                print(f"Error loading config file: {e}")
                self.config = {}
        elif not self.config:
            print("Config not provided. Using default values.")
            self.config = {
                "ecg_filter_config": {
                    "powerline_interference_frequency": 50,
                    "notch_filter_quality_factor": 30
                }
            }

    def set_sqa_result(self, sqa_result:dict,sqa_mask=None):
        """Optional setter for injecting SQA analysis externally."""
        self.sqa_result = sqa_result
        self.sqa_mask = sqa_mask    
        
    @staticmethod
    def remove_baseline_wander(raw_signal, fs, cutoff=0.5, order=2):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
        return signal.filtfilt(b, a, raw_signal)

    @staticmethod
    def remove_powerline_interference(raw_signal, fs, notch_freq=50, quality_factor=30):
        nyq = 0.5 * fs
        w0 = notch_freq / nyq
        b, a = signal.iirnotch(w0, quality_factor)
        return signal.filtfilt(b, a, raw_signal)

    @staticmethod
    def remove_muscle_artifacts_and_electrode_motion(raw_signal, fs, low_cut=0.5, high_cut=45, order=4):
        nyq = 0.5 * fs
        low = low_cut / nyq
        high = high_cut / nyq
        b, a = signal.butter(order, [low, high], btype='band')
        return signal.filtfilt(b, a, raw_signal)

    def fit(self, X, y=None):
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Apply filters based on SQA results.
        """
        if self.sqa_result is None:
            raise ValueError("SQA result not set. Use `.set_sqa_result()` or pass in constructor.")

        # STEP 1: Baseline Wander Removal
        if self.sqa_result.get("baseline", {}).get("bw_present", False):
            X = self.remove_baseline_wander(X, self.fs, cutoff=self.lowcut, order=self.order)

        # STEP 2: Powerline Interference
        notch_freq = self.config["ecg_filter_config"].get("powerline_interference_frequency", 50)
        q_factor = self.config["ecg_filter_config"].get("notch_filter_quality_factor", 30)

        if self.sqa_result.get("hf_noise", {}).get("avg_hf_ratio", 0) > 0.1:
            X = self.remove_powerline_interference(X, self.fs, notch_freq, q_factor)

        # STEP 3: Muscle/Electrode Artifacts
        if self.sqa_result.get("hf_noise", {}).get("prob_noisy", 0) > 0.3:
            X = self.remove_muscle_artifacts_and_electrode_motion(X, self.fs,
                                                                   low_cut=self.lowcut,
                                                                   high_cut=self.highcut,
                                                                   order=self.order)

        return X
