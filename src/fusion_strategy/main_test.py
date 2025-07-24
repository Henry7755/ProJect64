import sys
from pathlib import Path

# Go 2 levels up from current file to reach the root project folder
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / 'src'))

from src.fusion_strategy.WFDBSignalProcessor import WFDBSignalProcessor

if __name__ == "__main__":
    sp = WFDBSignalProcessor("/home/psyche/Documents/ProJect64/ProJect64 System Architect/src/config/vae_data_config.yaml")
    data = sp.process_all()
    #print("Preprocessing complete. Data shape:", data.shape)
    for signal_name, signal_array in data.items():
     print(f"{signal_name} shape: {signal_array.shape}")
