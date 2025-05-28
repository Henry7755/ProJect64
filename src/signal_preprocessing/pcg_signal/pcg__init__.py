from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import scipy.signal as sig
import yaml

class PCGfilter( BaseEstimator, TransformerMixin):
    """Class for handling noise in PCG signals."""
    def __init__(self, fs, lowcut=20, highcut=400, order=4, config_path=None):
        self.fs = fs
        self.lowcut = lowcut
        self.highcut = highcut
        self.order = order
        self.config_path = config_path
        
        if self.config_path:
            try:
                with open(self.config_path, 'r') as file:
                    self.config = yaml.safe_load(file)
            except Exception as e:
                print(f"Error loading config file: {e}")
                self.config = {}  # Set to empty dict to avoid errors.  Handle this more robustly in a real application.
        else:
             print("Config path not provided.  Using default parameters.")
             self.config = {}

    
        
   
    def bandpass(self, signal, filter_type='butter'):
        nyquist = 0.5 * self.fs
        low = self.lowcut / nyquist
        high = self.highcut / nyquist

       

       
        sos = sig.butter(self.order, [low, high], btype='bandpass', output='sos')
        return sig.sosfilt(sos, signal)
       
       
    def fit(self, X, y=None):
        return self
    
    
    def transform(self, X):
        Y = self.bandpass(signal = X, filter_type='butter')
       
    
        return Y
    

