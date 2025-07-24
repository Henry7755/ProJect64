import numpy as np
import pandas as pd
from pathlib import Path

from src.utils.file_utils import load_yaml, get_base_dir
from src.signal_preprocessing.ecg_noise_control import ECGfilter
from src.signal_preprocessing.pcg_noise_control import PCGfilter
from src.signal_preprocessing.SignalQualityAssesment import UnifiedSignalSQA

class SignalPreprocessor:
    def __init__(self, config_path="config/vae_data_config.yaml"):
        base_dir = get_base_dir()
        config_file = base_dir / config_path
        config = load_yaml(config_file)["preprocessing"]

        self.window_size = config["window_size"]
        self.stride = int(self.window_size * (1 - config["overlap"]))
        self.normalize = config["normalize"]
        self.signals = config["signals"]

        # # Handle multiple output paths for each signal
        # output_paths = config["output_path"]
        # if isinstance(output_paths, list):
        #     self.output_paths = {
        #         sig: (base_dir / Path(p)).resolve()
        #         for sig, p in zip(self.signals, output_paths)
        #     }
        # else:
        #     self.output_paths = {
        #         self.signals[0]: (base_dir / Path(output_paths)).resolve()
        #     }


        # Handle multiple or single output paths for each signal
        output_paths = config["output_path"]

        if isinstance(output_paths, list):
            if len(output_paths) != len(self.signals):
                raise ValueError("Length of output_path list must match number of signals")
            self.output_paths = {
                sig.upper(): (base_dir / Path(p)).resolve()
                for sig, p in zip(self.signals, output_paths)
            }
        else:
            shared_path = (base_dir / Path(output_paths)).resolve()
            self.output_paths = {
                sig.upper(): shared_path for sig in self.signals
            }


        self.input_folder = (base_dir / config["input_folder"]).resolve()
        self.save_numpy = config.get("save_numpy", True)

    def _normalize_signal(self, x):
        if self.normalize == "zscore":
            return (x - np.mean(x)) / (np.std(x) + 1e-8)
        elif self.normalize == "minmax":
            return (x - np.min(x)) / (np.max(x) - np.min(x) + 1e-8)
        return x

    def _process_signal(self, s, raw_signal):
        raw_signal = self._normalize_signal(raw_signal)

        if "ecg" in s.lower():
            fs = 500
            sqa = UnifiedSignalSQA(raw_signal, fs=fs, signal_type='ecg')
            analysis = sqa.analyze()

            sqa_mask = np.ones(len(raw_signal), dtype=bool)
            for start_sec, end_sec in analysis["flatline_segments"]:
                start = int(start_sec * fs)
                end = int(end_sec * fs)
                sqa_mask[start:end] = False

            filt = ECGfilter(fs=fs)
            filt.set_sqa_result(analysis,sqa_mask = sqa_mask)
            filtered = filt.transform(raw_signal)

        elif "pcg" in s.lower():
            fs = 1000
            sqa = UnifiedSignalSQA(raw_signal, fs=fs, signal_type='pcg')
            analysis = sqa.analyze()

            sqa_mask = np.ones(len(raw_signal), dtype=bool)
            if analysis.get("clipping_detected", False):
                sqa_mask[:] = False  # crude approach if totally clipped

            filt = PCGfilter(fs=fs)
            filt.set_sqa_result(analysis,sqa_mask = sqa_mask)
            filtered = filt.transform(raw_signal)

        else:
            filtered = raw_signal  # fallback

        return filtered

    def _segment(self, signal):
        segments = []
        for start in range(0, len(signal) - self.window_size + 1, self.stride):
            window = signal[start:start + self.window_size]
            segments.append(window)
        return np.array(segments)

    def process_file(self, file_path):
        df = pd.read_csv(file_path)
        signal_segments = {}

        for s in self.signals:
            if s not in df.columns:
                raise ValueError(f"Signal {s} not found in file {file_path.name}")

            raw = df[s].values
            filtered = self._process_signal(s, raw)
            segments = self._segment(filtered)

            if s not in signal_segments:
                signal_segments[s] = []
            signal_segments[s].append(segments)

        return signal_segments


    def process_all(self):
        merged = {sig: [] for sig in self.signals}

        for file in self.input_folder.glob("*.csv"):
            print(f"Processing: {file.name}")
            sig_segments = self.process_file(file)
            for sig in self.signals:
                # Collect all segments for each signal
                merged[sig].append(sig_segments[sig][0])

        for sig in self.signals:
            data = np.vstack(merged[sig])  # Stack all windows for the signal
            if self.save_numpy:
                out_path = self.output_paths[sig]
                out_path.parent.mkdir(parents=True, exist_ok=True)
                np.save(str(out_path), data)  # ✅ Corrected from output_paths to out_path
                print(f"Saved {sig} data to {out_path}")

        # ✅ Return final dictionary of stacked signal data
        return {sig: np.vstack(merged[sig]) for sig in self.signals}
