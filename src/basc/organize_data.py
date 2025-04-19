# --------------------------------------
# If your source folder contains files for multiple end users, you can use the following code to organize them into subfolders based on the pattern BASC-PX-... 
# (e.g., BASC-P1-2025-Mother).
# This script will create subfolders for each unique pattern and move the files accordingly.
# --------------------------------------
import os
import shutil
import re

# Set this to the directory where your files are
directory = '../../data/basc_poc'

# Make sure the directory exists
if not os.path.isdir(directory):
    raise ValueError(f"Directory {directory} does not exist.")

# Go through each file in the directory
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)

    # Skip if it's a directory
    if os.path.isdir(file_path):
        continue

    # Match the pattern BASC-PX-... (e.g., BASC-P1-2025-Mother)
    match = re.match(r'BASC-(P\d+)-', filename)
    if match:
        folder_name = match.group(1)
        target_folder = os.path.join(directory, folder_name)

        # Create the subfolder if it doesn't exist
        os.makedirs(target_folder, exist_ok=True)

        # Move the file
        shutil.move(file_path, os.path.join(target_folder, filename))
        print(f"Moved {filename} → {target_folder}")
    else:
        print(f"Skipped {filename}, no matching pattern.")
