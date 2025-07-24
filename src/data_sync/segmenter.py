import numpy as np
import os
import pandas as pd
import logging

# --- Setup Logging ---
# Configures the logging system to write messages to 'segmentation_log.txt'.
# It captures INFO level messages and above, formatting them with timestamp, level, and message.
logging.basicConfig(
    filename="segmentation_log.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# --- Configuration ---
# Defines constants for signal processing.
SAMPLE_RATE = 1000  # Samples per second
WINDOW_DURATION = 10.0  # seconds, duration of each segment
WINDOW_SIZE = int(SAMPLE_RATE * WINDOW_DURATION)  # Total number of samples in a window
# Minimum length of the signal for non-overlapping segmentation.
# If the signal is shorter than this, 50% overlap will be applied.
MIN_LEN_NON_OVERLAP = 3 * WINDOW_SIZE
# Directory where the raw, synched data files are located.
DATA_DIR = r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Synched_Data"

# --- Output Directories ---
# Base directory for saving segmented CSV files.
base_output_dir = r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\segments_csv"
# Specific directories for 'Before' and 'After' activity segments.
before_dir = os.path.join(base_output_dir, "Before")
after_dir = os.path.join(base_output_dir, "After")

# Create the output directories if they do not already exist.
# exist_ok=True prevents an error if the directory already exists.
os.makedirs(before_dir, exist_ok=True)
os.makedirs(after_dir, exist_ok=True)

# --- Load and Prepare Demographics ---
# Loads the demographics file and prepares the data for processing.
try:
    file_path = r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Rel_Sourcing.csv"
    # Reads the CSV file, specifying that the header is on the second row (index 1).
    rel_source = pd.read_csv(file_path)

    records = zip(rel_source["FileName"], rel_source["Activity"])

# --- Error Handling for Demographics Loading ---
except FileNotFoundError:
    # Logs an error if the demographics file is not found.
    logging.error(f"Demographics file not found at: {file_path}")
    raise  # Re-raises the exception to stop execution if the file is critical.
except KeyError as e:
    # Logs an error if an expected column is missing in the demographics file.
    logging.error(f"Missing expected column in Demographics.csv: {e}")
    raise
except Exception as e:
    # Catches any other general exceptions during demographics loading.
    logging.error(f"Failed to load or process demographics file: {e}")
    raise

# --- Smart Segmentation Function ---
def smart_segment_multimodal(signal: np.ndarray) -> list:
    """
    Segments a 2-channel signal (e.g., ECG and PCG) into fixed-size windows.
    Applies 50% overlap if the total signal length is less than MIN_LEN_NON_OVERLAP,
    otherwise uses no overlap.

    Args:
        signal (np.ndarray): A 2D NumPy array where signal.shape = (2, total_samples).
                             Row 0 is ECG, Row 1 is PCG.

    Returns:
        List[np.ndarray]: A list of segmented signal windows, each of shape (2, WINDOW_SIZE).
    """
    total_len = signal.shape[1]  # The total number of samples in the signal (columns).

    # If the signal is too short to even form one window, log a warning and return an empty list.
    if total_len < WINDOW_SIZE:
        logging.warning(f"Signal (length: {total_len}) is too short for a single window of size {WINDOW_SIZE}. Skipping segmentation.")
        return []

    # Corrected: Determine step size based on total signal length relative to MIN_LEN_NON_OVERLAP.
    # If the signal is shorter than MIN_LEN_NON_OVERLAP, use 50% overlap.
    if total_len < MIN_LEN_NON_OVERLAP:
        step = WINDOW_SIZE // 2  # 50% overlap (step size is half the window size)
        logging.info(f"Signal length ({total_len}) is less than {MIN_LEN_NON_OVERLAP}, using 50% overlap (step size: {step}).")
    else:
        # Otherwise, use no overlap (step size is equal to the window size).
        step = WINDOW_SIZE
        logging.info(f"Signal length ({total_len}) is sufficient, using no overlap (step size: {step}).")

    segments = []
    # Iterate through the signal to create segments.
    # The loop stops when a full window cannot be formed from the remaining signal.
    for i in range(0, total_len - WINDOW_SIZE + 1, step):
        segments.append(signal[:, i:i + WINDOW_SIZE])

    return segments

# --- Process Each Signal ---
# Initialize counters for segment IDs for 'before' and 'after' activities.
before_id, after_id = 1, 1

# Iterates through each record obtained from the demographics file.
for synced_file, activity in records:
    path = os.path.join(DATA_DIR, synced_file)  # Constructs the full path to the synched data file.

    # Checks if the current data file exists. If not, logs a warning and skips to the next file.
    if not os.path.exists(path):
        logging.warning(f"File not found: {path}. Skipping.")
        continue

    logging.info(f"Processing file: {synced_file} (Activity: {activity})")
    try:
        # Reads the synched data file into a Pandas DataFrame.
        df = pd.read_csv(path)

        # Corrected: Check if both 'ECG' and 'PCG' columns are present.
        required_columns = ["ECG", "PCG"]
        if not all(col in df.columns for col in required_columns):
            logging.warning(f"Missing one or more required columns (ECG, PCG) in {synced_file}. Skipping.")
            continue

        # Extracts 'ECG' and 'PCG' columns, converts to a NumPy array, and transposes it.
        # The .T.values ensures the shape is (channels, time) which is expected by smart_segment_multimodal.
        signal = df[required_columns].T.values  # shape: (2, time)
        # Calls the segmentation function.
        segments = smart_segment_multimodal(signal)

        logging.info(f"Found {len(segments)} segments in {synced_file}.")

        # If no segments were generated (e.g., signal too short), log and continue.
        if not segments:
            logging.info(f"No segments generated for {synced_file}.")
            continue

        # Iterates through each generated segment.
        for seg_array in segments:
            # Converts the NumPy segment array back into a Pandas DataFrame for saving.
            # Transposes back to (time, channels) and assigns column names.
            df_seg = pd.DataFrame(seg_array.T, columns=["ECG", "PCG"])

            # Determines the output path and increments the appropriate ID based on the activity type.
            # .strip().lower().startswith("b") handles variations like "Before ", "b", "B".
            if activity.strip().lower().startswith("b"):
                out_path = os.path.join(before_dir, f"before_{before_id:03d}.csv")
                before_id += 1
            else:  # Assumes any other activity is "After" (e.g., "A", "After ").
                out_path = os.path.join(after_dir, f"after_{after_id:03d}.csv")
                after_id += 1

            # Saves the segmented DataFrame to a CSV file. index=False prevents writing the DataFrame index.
            df_seg.to_csv(out_path, index=False)
            logging.info(f"Saved segment to {out_path}")

    # --- Specific Error Handling for File Processing ---
    except pd.errors.EmptyDataError:
        # Catches error if the CSV file is empty.
        logging.error(f"File is empty: {path}. Skipping.")
    except pd.errors.ParserError:
        # Catches error if the CSV file cannot be parsed.
        logging.error(f"Could not parse file: {path}. Skipping.")
    except Exception as e:
        # Catches any other unexpected errors during processing of a specific file.
        # exc_info=True includes the full traceback in the log for better debugging.
        logging.error(f"An unexpected error occurred while processing {synced_file}: {e}", exc_info=True)

# Logs a message indicating the completion of the entire segmentation process.
logging.info("Segmentation process completed.")
