import shutil
import os

# Define the source and destination folder paths
source_folder = "C:/Users/abusu/Desktop/BME/Semester 7/ProJect64/ProJect64 System Architect/Data/CSV"  # Change this to your source folder
destination_folder = "C:/Users/abusu/Desktop/BME/Semester 7/ProJect64/ProJect64 System Architect/Data/Rel_Data"  # Change this to your target folder

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Loop through files in the source folder
for file_name in os.listdir(source_folder):
    if file_name.lower().endswith(".csv") and ("pcg" in file_name.lower() or "ecg" in file_name.lower()):
        source_file = os.path.join(source_folder, file_name)
        destination_file = os.path.join(destination_folder, file_name)

        # Move the file
        shutil.move(source_file, destination_file)
        print(f"Moved: {file_name} to {destination_folder}")

print("File moving process completed.")