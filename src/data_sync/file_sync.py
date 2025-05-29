import os
import re

def group_signal_files_by_timestamp(directory_path):
    """
    Groups signal files (acc, ecg, pcg) by their unique timestamps.

    Args:
        directory_path (str): The path to the directory containing the signal files.

    Returns:
        dict: A dictionary where keys are timestamps (e.g., '1_10-09-54')
              and values are dictionaries containing the file paths for
              'acc', 'ecg', and 'pcg' for that timestamp.
              Example:
              {
                  '1_10-09-54': {
                      'acc': 'path/to/1_10-09-54_acc.csv',
                      'ecg': 'path/to/1_10-09-54_ecg.csv',
                      'pcg': 'path/to/1_10-09-54_pcg.csv'
                  },
                  '1_10-11-48': { ... }
              }
    """
    grouped_files = {}
    
    # Regex to extract timestamp and signal type
    # Example: '1_10-09-54_acc.csv' -> timestamp: '1_10-09-54', type: 'acc'
    filename_pattern = re.compile(r'^(?P<timestamp>\d{1,2}_\d{2}-\d{2}-\d{2})_(?P<signal_type>acc|ecg|pcg)\.csv$')

    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return {}

    for filename in os.listdir(directory_path):
        match = filename_pattern.match(filename)
        if match:
            timestamp = match.group('timestamp')
            signal_type = match.group('signal_type')
            full_filepath = os.path.join(directory_path, filename)

            if timestamp not in grouped_files:
                grouped_files[timestamp] = {}
            
            # Store the full path for the specific signal type
            grouped_files[timestamp][signal_type] = full_filepath
        else:
            print(f"Skipping file: {filename} (does not match expected pattern)")

    return grouped_files

def process_signals_for_timestamp(timestamp, file_paths_dict):
    """
    Placeholder function to process the acc, ecg, and pcg files for a given timestamp.
    You'll replace this with your actual signal processing logic.

    Args:
        timestamp (str): The unique timestamp for the current set of files.
        file_paths_dict (dict): A dictionary containing 'acc', 'ecg', 'pcg' file paths.
    """
    print(f"\n--- Processing for Timestamp: {timestamp} ---")
    
    acc_file = file_paths_dict.get('acc')
    ecg_file = file_paths_dict.get('ecg')
    pcg_file = file_paths_dict.get('pcg')

    if acc_file:
        print(f"  ACC file: {acc_file}")
        # import pandas as pd
        # acc_data = pd.read_csv(acc_file)
        # Your ACC processing logic here
    else:
        print("  ACC file missing for this timestamp.")

    if ecg_file:
        print(f"  ECG file: {ecg_file}")
        # ecg_data = pd.read_csv(ecg_file)
        # Your ECG processing logic here
    else:
        print("  ECG file missing for this timestamp.")

    if pcg_file:
        print(f"  PCG file: {pcg_file}")
        # pcg_data = pd.read_csv(pcg_file)
        # Your PCG processing logic here
    else:
        print("  PCG file missing for this timestamp.")

    # Example: You might want to load all three, align them, and then process
    # if acc_file and ecg_file and pcg_file:
    #     acc_data = pd.read_csv(acc_file)
    #     ecg_data = pd.read_csv(ecg_file)
    #     pcg_data = pd.read_csv(pcg_file)
    #     # Perform combined analysis, synchronization, etc.
    #     print(f"  Successfully loaded all three files for {timestamp}")
    # else:
    #     print(f"  One or more signal files missing for {timestamp}. Cannot perform combined analysis.")


# --- Main execution ---
if __name__ == "__main__":
    # Create a dummy directory and files for demonstration if they don't exist
    dummy_dir = r"C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Rel_Data"
    if not os.path.exists(dummy_dir):
        os.makedirs(dummy_dir)
        print(f"Created dummy directory: {dummy_dir}")
        dummy_files = [
            "1_10-09-54_acc.csv", "1_10-09-54_ecg.csv", "1_10-09-54_pcg.csv",
            "1_10-11-48_acc.csv", "1_10-11-48_ecg.csv", "1_10-11-48_pcg.csv",
            "1_10-12-41_acc.csv", "1_10-12-41_ecg.csv", "1_10-12-41_pcg.csv",
            "1_10-25-13_acc.csv", "1_10-25-13_ecg.csv", "1_10-25-13_pcg.csv",
            "1_10-26-08_acc.csv", "1_10-26-08_ecg.csv", # Note: pcg missing for this one to show robustness
            "another_file.txt" # This will be skipped by the regex
        ]
        for f in dummy_files:
            with open(os.path.join(dummy_dir, f), 'w') as temp_f:
                temp_f.write("dummy,data\n1,2\n") # Write some dummy content

    # Replace 'signals_data' with the actual path to your directory
    signals_directory = r'C:\Users\abusu\Desktop\BME\ProJect64\ProJect64 System Architect\Data\Rel_Data' 
    
    # Group the files
    grouped_signal_data = group_signal_files_by_timestamp(signals_directory)

    # Print the grouped structure (for debugging/verification)
    print("\n--- Grouped Files Structure ---")
    for timestamp, files_dict in grouped_signal_data.items():
        print(f"Timestamp: {timestamp}, Files: {files_dict}")
    print("------------------------------")

    # Process each group of files
    print("\n--- Starting Signal Processing ---")
    for timestamp, file_paths in sorted(grouped_signal_data.items()):
        process_signals_for_timestamp(timestamp, file_paths)
    print("\n--- Signal Processing Complete ---")