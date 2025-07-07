import sys
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from  signal_preprocessing import ECGfilter
from signal_preprocessing.SignalQualityAssesment import UnifiedSignalSQA
import pandas as pd


# Add src/ to the system path
sys.path.append(str(Path(__file__).resolve().parents[2]))  

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / 'config'/'meta_ecg.yaml'

from utils.file_utils import load_yaml
from utils import Normalize

config = load_yaml(CONFIG_PATH)
df = pd.read_csv(r'C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Synched_Data\24_14-21-14_synced.csv')
ecg_array = df['ECG'].values


# For ECG
sqa_ecg = UnifiedSignalSQA(ecg_array, fs=500, signal_type='ecg')
result_ecg = sqa_ecg.analyze()
                                       
# Create a pipeline with the ECGNoiseHandler class
pipeline = Pipeline([('noise_handler', ECGfilter( lowcut=0.5,
                                                  highcut=50.0,
                                                  fs=config["ecg_filter_config"]["sampling_frequency"],
                                                  config_path=CONFIG_PATH ,
                                                  sqa_result=result_ecg)),
                     ("Normalization", FunctionTransformer(Normalize.normalize_signal))
])


# filt = ECGfilter(fs=500, config_path=zonfig_path)
# filt.set_sqa_result(result_ecg)
# filtered_signal = filt.transform(ecg_array)