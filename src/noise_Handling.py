import numpy as np

class ECGNoiseHandling :
    def __init__(self, signal, sampling_freq, ): 
        self.signal = signal
        self.sampling_freq = sampling_freq
        self.noise = None

    def remove_baseline_wander(self):
        """ Removing Baseline Wander using high pass filter """
        pass
    
    def remove_powerline_interference(self):
        """ Removing Powerline Interference using notch filter """
        pass
    
    def remove_ma_El(self):
        """ Removing Muscles artefacts and Electrode Motion"""
        pass