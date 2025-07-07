import sys
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from  signal_preprocessing import PCGfilter
from signal_preprocessing.SignalQualityAssesment import UnifiedSignalSQA 
import pandas as pd   



# Add src/ to the system path
sys.path.append(str(Path(__file__).resolve().parents[2]))  
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / 'config'/'meta_pcg.yaml'

from utils.file_utils import load_yaml
from utils import Normalize

config = load_yaml(CONFIG_PATH)
df = pd.read_csv(r'C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Synched_Data\24_14-21-14_synced.csv')
pcg_array = df['PCG'].values
sqa_pcg = UnifiedSignalSQA(pcg_array, fs=1000, signal_type='pcg')
result_pcg = sqa_pcg.analyze()

pipeline = Pipeline([ ("Normalization", FunctionTransformer(Normalize.normalize_signal)),
                      ("noise_handler", PCGfilter(fs = config["signal"]["Sampling_rate"],
                                lowcut = config["preprocessing"]["bandpass_filter"]["lowcut"],
                                highcut= config["preprocessing"]["bandpass_filter"]["highcut"],
                                order= config["preprocessing"]["bandpass_filter"]["order"],
                                config_path=CONFIG_PATH,
                                sqa_result=result_pcg))
    ])

