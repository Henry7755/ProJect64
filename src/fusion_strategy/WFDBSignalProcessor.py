import os
import wfdb
import numpy as np
from scipy.io import wavfile
from pathlib import Path
import yaml
from scipy.stats import zscore

class WFDBSignalProcessor:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.segment_length = self.config["preprocessing"]["window_size"]
        self.overlap = self.config["preprocessing"]["overlap"]
        self.normalize = self.config["preprocessing"]["normalize"]
        self.signals = [s.upper() for s in self.config["preprocessing"]["signals"]]
        self.input_folder = Path(self.config["preprocessing"]["input_folder"])
        self.output_paths = self.config["preprocessing"]["output_path"]
        self.save_numpy = self.config["preprocessing"].get("save_numpy", False)

    def _load_config(self, path):
        with open(path, "r") as file:
            return yaml.safe_load(file)

    def _segment(self, signal):
        step = int(self.segment_length * (1 - self.overlap))
        segments = []
        for start in range(0, len(signal) - self.segment_length + 1, step):
            segment = signal[start:start + self.segment_length]
            if self.normalize == "zscore":
                segment = zscore(segment)
            segments.append(segment)
        return np.array(segments) if segments else None

    def process_all(self):
        hea_files = sorted(self.input_folder.glob("*.hea"))
        print(f"📁 Found {len(hea_files)} records to process.")

        for hea_file in hea_files:
            record_name = hea_file.stem
            try:
                record = wfdb.rdrecord(str(self.input_folder / record_name))
            except Exception as e:
                print(f"❌ Failed to read {record_name}: {e}")
                continue

            print(f"\n📂 Processing: {record_name}")
            print(f"   Signals: {record.sig_name}")
            print(f"   Signal Length: {len(record.p_signal)}")

            record_sig_names = [s.upper() for s in record.sig_name]
            for sig_type in self.signals:
                try:
                    if sig_type == "PCG":
                        wav_path = self.input_folder / f"{record_name}.wav"
                        fs, raw = wavfile.read(str(wav_path))
                    elif sig_type == "ECG":
                        idx = record_sig_names.index(sig_type)
                        raw = record.p_signal[:, idx]
                    else:
                        continue

                    segments = self._segment(raw)
                    if segments is None:
                        print(f"[WARNING] No valid segments for {sig_type}. Skipping save.")
                        continue

                    print(f"   ✅ {sig_type}: {segments.shape[0]} segments")

                    if self.save_numpy:
                        save_dir = Path(self.output_paths[self.signals.index(sig_type)])
                        save_dir.mkdir(parents=True, exist_ok=True)
                        save_path = save_dir / f"{record_name}_{sig_type}.npy"
                        np.save(save_path, segments)
                        print(f"   💾 Saved {sig_type} segments to {save_path}")

                except Exception as e:
                    print(f"   ❌ Error processing {sig_type} for {record_name}: {e}")

