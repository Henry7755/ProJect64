import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import re
import logging
from data_sync  import prototype_sync as pys


# Basic configuration
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detail
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("processing_log.txt")
    ]
)


def group_signal_files_by_timestamp(directory_path):
    """
    Groups signal files (acc, ecg, pcg) by their unique timestamps.
    """
    grouped_files = {}

    filename_pattern = re.compile(r'^(?P<timestamp>\d{1,2}_\d{2}-\d{2}-\d{2})_(?P<signal_type>acc|ecg|pcg)\.csv$')

    if not os.path.isdir(directory_path):
        logging.error(f"Directory '{directory_path}' not found.")
        return {}

    for filename in os.listdir(directory_path):
        match = filename_pattern.match(filename)
        if match:
            timestamp = match.group('timestamp')
            signal_type = match.group('signal_type')
            full_filepath = os.path.join(directory_path, filename)

            if timestamp not in grouped_files:
                grouped_files[timestamp] = {}

            grouped_files[timestamp][signal_type] = full_filepath
        else:
            logging.warning(f"Skipping file: {filename} (does not match expected pattern)")

    return grouped_files


def process_signals_for_timestamp(timestamp, file_paths_dict, save_dir):
    """
    Load and synchronize signals for a given timestamp, then save to CSV.
    """
    logging.info(f"Processing timestamp: {timestamp}")

    try:
        signals = []
        labels = []

        for signal_type in ['ecg', 'pcg', 'acc']:
            file_path = file_paths_dict.get(signal_type)
            if file_path and os.path.exists(file_path):
                time, signal = pys.load_signal(file_path)
                signals.append((time, signal))
                labels.append(signal_type.upper())
                logging.info(f"Loaded {signal_type.upper()} file: {file_path}")
            else:
                logging.warning(f"{signal_type.upper()} file missing for timestamp {timestamp}")

        if len(signals) < 2:
            logging.warning(f"Insufficient signals to synchronize for timestamp {timestamp}")
            return

        # Synchronize
        t_common, synced_signals = pys.synchronize_signals(signals, fs_common=1000)

        # Stack and save
        synced_matrix = pys.np.vstack(synced_signals).T
        df = pys.pd.DataFrame(synced_matrix, columns=labels)
        df['Time'] = t_common
        df = df[['Time'] + labels]  # Time first

        save_path = os.path.join(save_dir, f"{timestamp}_synced.csv")
        df.to_csv(save_path, index=False)
        logging.info(f"Synchronized data saved to: {save_path}")

        # Optional plotting
        # plot_signals(t_common, synced_signals, labels)

    except Exception as e:
        logging.error(f"Failed processing {timestamp}: {e}")


    # Example placeholder for future logic
    # if acc_file and ecg_file and pcg_file:
    #     logging.info(f"All files available for timestamp {timestamp}, proceeding with processing.")
    # else:
    #     logging.warning(f"Cannot process {timestamp} due to missing file(s).")


# --- Main execution ---
if __name__ == "__main__":
    dummy_dir = r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Rel_Data"
    if not os.path.exists(dummy_dir):
        os.makedirs(dummy_dir)
        logging.info(f"Created dummy directory: {dummy_dir}")
        dummy_files = [
            "1_10-09-54_acc.csv", "1_10-09-54_ecg.csv", "1_10-09-54_pcg.csv",
            "1_10-11-48_acc.csv", "1_10-11-48_ecg.csv", "1_10-11-48_pcg.csv",
            "1_10-12-41_acc.csv", "1_10-12-41_ecg.csv", "1_10-12-41_pcg.csv",
            "1_10-25-13_acc.csv", "1_10-25-13_ecg.csv", "1_10-25-13_pcg.csv",
            "1_10-26-08_acc.csv", "1_10-26-08_ecg.csv",  # PCG missing here
            "another_file.txt"
        ]
        for f in dummy_files:
            with open(os.path.join(dummy_dir, f), 'w') as temp_f:
                temp_f.write("dummy,data\n1,2\n")

    signals_directory = r'C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Rel_Data'

    grouped_signal_data = group_signal_files_by_timestamp(signals_directory)
    save_directory =r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Synched_Data"

    logging.info("--- Grouped Files Structure ---")
    for timestamp, files_dict in grouped_signal_data.items():
        logging.info(f"Timestamp: {timestamp}, Files: {files_dict}")
    logging.info("------------------------------")

    logging.info("--- Starting Signal Processing ---")
    for timestamp, file_paths in sorted(grouped_signal_data.items()):
        process_signals_for_timestamp(timestamp, file_paths,save_directory)
    logging.info("--- Signal Processing Complete ---")
