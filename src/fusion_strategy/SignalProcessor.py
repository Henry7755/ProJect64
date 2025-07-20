import numpy as np
import pandas as pd
from pathlib import Path
from utils.file_utils import load_yaml, get_base_dir  # Adjust to your actual utils path
from signal_preprocessing.ecg_noise_control import ECGfilter
from signal_preprocessing.pcg_noise_control import PCGfilter

class SignalPreprocessor:
    def __init__(self, config_path="config/vae_data_config.yaml"):
        base_dir = get_base_dir()
        config_file = base_dir / config_path
        config = load_yaml(config_file)["preprocessing"]

        self.window_size = config["window_size"]
        self.stride = int(self.window_size * (1 - config["overlap"]))
        self.normalize = config["normalize"]
        self.signals = config["signals"]

        # Paths relative to project root
        self.input_folder = (base_dir / config["input_folder"]).resolve()
        self.output_path = (base_dir / config["output_path"]).resolve()
        self.save_numpy = config.get("save_numpy", True)

    def _normalize_signal(self, x):
        if self.normalize == "zscore":
            return (x - np.mean(x)) / (np.std(x) + 1e-8)
        elif self.normalize == "minmax":
            return (x - np.min(x)) / (np.max(x) - np.min(x) + 1e-8)
        return x

        # ...existing code...
    def process_file(self, file_path):
        df = pd.read_csv(file_path)
        channels = []
        for s in self.signals:
            signal = self._normalize_signal(df[s].values)
            # Example: Apply ECG or PCG filter based on signal name
            if "ecg" in s.lower():
                filt = ECGfilter(fs=500)  # Set fs and config as needed
                # Optionally set SQA result: filt.set_sqa_result(sqa_result)
                signal = filt.transform(signal)
            elif "pcg" in s.lower():
                filt = PCGfilter(fs=1000)  # Set fs and config as needed
                # Optionally set SQA result: filt.set_sqa_result(sqa_result)
                signal = filt.transform(signal)
            channels.append(signal)
        num_samples = len(channels[0])
    
        segments = []
        for start in range(0, num_samples - self.window_size + 1, self.stride):
            window = np.concatenate([ch[start:start + self.window_size] for ch in channels])
            segments.append(window)
    
        return np.array(segments)
    # ...existing code...def process_file(self, file_path):
      

    def process_all(self):
        all_segments = []
        for file in self.input_folder.glob("*.csv"):
            print(f"Processing: {file.name}")
            segments = self.process_file(file)
            all_segments.append(segments)

        data = np.vstack(all_segments)

        if self.save_numpy:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(self.output_path, data)
            print(f"Saved to {self.output_path}")

        return data
