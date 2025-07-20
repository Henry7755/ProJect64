import sys
from pathlib import Path

# Go 2 levels up from current file to reach the root project folder
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / 'src'))

from fusion_strategy.SignalProcessor import SignalPreprocessor


from fusion_strategy.SignalProcessor import SignalPreprocessor

if __name__ == "__main__":
    sp = SignalPreprocessor("src/config/vae_data_config.yaml")
    data = sp.process_all()
    print("Preprocessing complete. Data shape:", data.shape)
