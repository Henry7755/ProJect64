# -*- coding: utf-8 -*-
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
from scipy.signal import butter, filtfilt, iirnotch

class ECGfilter(BaseEstimator, TransformerMixin):
    """Class for handling noise in ECG signals."""
     def __init__(self, fs=500, lowcut=0.5, highcut=45, order=4):
        self.fs = fs
        self.lowcut = lowcut
        self.highcut = highcut
        self.order = order

    @staticmethod
    def remove_baseline_wander(raw_signal, fs, cutoff=0.5, order=2):
        """Removing Baseline Wander using high pass filter."""
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
        filtered_signal = signal.filtfilt(b, a, raw_signal)
        return filtered_signal

    @staticmethod
    def remove_powerline_interference(raw_signal, fs, notch_freq=50, quality_factor=30):
        """Removing Powerline Interference using notch filter."""
        nyq = 0.5 * fs
        w0 = notch_freq / nyq
        b, a = signal.iirnotch(w0, quality_factor)
        filtered_signal = signal.filtfilt(b, a, raw_signal)
        return filtered_signal

    @staticmethod
    def remove_muscle_artifacts_and_electrode_motion(raw_signal, fs, low_cut=0.5, high_cut=45, order=4):
        """Removing Muscles artefacts and Electrode Motion."""
        nyq = 0.5 * fs
        low = low_cut / nyq
        high = high_cut / nyq
        b, a = signal.butter(order, [low, high], btype='band')
        filtered_signal = signal.filtfilt(b, a, raw_signal)
        return filtered_signal

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        """Apply the filtering process to the ECG signal."""
        # Step 1: Remove Baseline Wander
        X = self.remove_baseline_wander(X, self.fs, cutoff=self.lowcut, order=self.order)
        
        # Step 2: Remove Powerline Interference
        X = self.remove_powerline_interference(X, self.fs, notch_freq=50, quality_factor=30)
        
        # Step 3: Remove Muscle Artifacts and Electrode Motion
        X = self.remove_muscle_artifacts_and_electrode_motion(X, self.fs, low_cut=self.lowcut, high_cut=self.highcut, order=self.order)
        
        return X
    

