import sys
from pathlib import Path
from sklearn.pipeline import Pipeline
from  ecg__init__ import ECGfilter
import pandas as pd



# Add src/ to the system path
sys.path.append(str(Path(__file__).resolve().parents[2]))  


BASE_DIR = Path(__file__).resolve().parents[2]


CONFIG_PATH = BASE_DIR / 'config'/'meta_ecg.yaml'

from utils.file_utils import load_yaml

config = load_yaml(CONFIG_PATH)



                                        
# Create a pipeline with the ECGNoiseHandler class
pipeline = Pipeline([
    ('noise_handler', ECGfilter( lowcut=0.5,
                                 highcut=50.0,
                                 fs=config["ecg_filter_config"]["sampling_frequency"],
                                 config_path=CONFIG_PATH ))
    
    #(Normalization()) 
    # (Timestamp())
    # (Resampling())
    # Add other transformations or models here as needed
])


df  = pd.read_csv(r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Rel_Data\1_10-09-54_ecg.csv")
# Tackle the ECG signal data but will call it in a different file
X_filtered = pipeline.fit_transform(df["lead_II"])

print (X_filtered)