from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import scipy.signal as sig
import yaml

class PCGfilter( BaseEstimator, TransformerMixin):
    """Class for handling noise in PCG signals."""
    def __init__( self, fs=1000, config = None, config_path=None): 
        self.fs = fs
        self.config = config
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

    @staticmethod
    def z_score_normalize(self,signal):
         """
  Performs z-score standardization on a signal.

  Args:
    signal (np.ndarray): The input PCG signal.

  Returns:
    np.ndarray: The standardized PCG signal.
  """
         mean_val = np.mean(signal)
         std_val = np.std(signal)
        
         if std_val == 0:
            standardized_signal = np.zeros_like(signal)
         else:
            standardized_signal = (signal - mean_val) / std_val

            return standardized_signal
        
    @staticmethod
    def bandpass (self, signal,lowcut, highcut, fs, order=4, filter_type='butter'):
        nyquist = 0.5 * fs  # Nyquist frequency
        low = lowcut / nyquist
        high = highcut / nyquist
        
        if filter_type == 'butter':
             sos = sig.butter(order, [low, high], btype='bandpass', analog=False, output='sos')
             filtered_data = sig.lfilter(sos, signal)
             return filtered_data
        else:
            raise ValueError("Unsupported filter type. Use 'butter' for Butterworth filter.")       
            print("Invalid filter type. Returning original data.")
        
        return signal
        
    @staticmethod
    def fit(self, X, y=None):
        return self
    
    
    def transform(self, X):
        """Apply the filtering process to the ECG signal."""
        # step 1: Apply z-score normalization
        X = self.z_score_normalize(X)
        
        # step 2: Apply bandpass filter
        X = self.bandpass(X,
                          lowcut=self.config["preprocessing"]["bandpass_filter"]["lowcut"],
                          highcut=self.config["preprocessing"]["bandpass_filter"]["highcut"],
                          fs=self.fs,
                          order=self.config["preprocessing"]["bandpass_filter"]["order"],
                          filter_type=self.config["preprocessing"]["bandpass_filter"]["filter_type"])
    
        return X
    

