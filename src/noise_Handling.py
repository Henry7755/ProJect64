import numpy as np
import scipy.signal as signal 

class ECGNoiseHandling :
    def __init__(self, signal, sampling_freq, ): 
        self.signal = signal
        self.sampling_freq = sampling_freq
        self.filtered_signal = None
        self.noise = None
     

    def remove_baseline_wander(self,cutoff=0.5, order=2):
        """ Removing Baseline Wander using high pass filter """
        nyquist = 0.5 * self.sampling_freq
        normal_cutoff = self.cutoff / nyquist
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
        self.filtered_signal = signal.filtfilt(b, a, self.raw_signal)
    
    def remove_powerline_interference(self, notch_freq=50, quality_factor=30):
        """ Removing Powerline Interference using notch filter """
        nyquist = 0.5 * self.sampling_rate
        w0 = notch_freq / nyquist
        b, a = signal.iirnotch(w0, quality_factor)
        self.filtered_signal = signal.filtfilt(b, a, self.filtered_signal if self.filtered_signal is not None else self.raw_signal)
     
    def remove_ma_El(self, low_cut=0.5, high_cut=45, order=4):
        """ Removing Muscles artefacts and Electrode Motion"""
        nyquist = 0.5 * self.sampling_rate
        low = low_cut / nyquist
        high = high_cut / nyquist
        b, a = signal.butter(order, [low, high], btype='band')
        self.filtered_signal = signal.filtfilt(b, a, self.filtered_signal if self.filtered_signal is not None else self.raw_signal)
        