"""This module contains helper functions for data processing in the Gormley Lab.
It includes a function to truncate SAXS data, check if files are in a folder"""


# ******************************************************************************
# This file is part of SAXS Assistant.
#
#    All code from SAXS Assisstant can be used freely for non-commercial purposes.
#    If you use this code in your work, please cite the following publications:
# Add The GPA citation
# Add Franke citation
# Add Raw citation
# SAXS Assistant citation
#    SAXS Assistant is based on the code from RAW, which is a SAXS data analysis software.
#
#
#    SAXS Assistant utilizes parts of the code from RAW
#    SAXS Assistant is shared for helping the community with SAXS data analysis.
#    but it is not a replacement for RAW, and does not include all the features of RAW.
#    SAXS Assisant does not offer warranty-- use at your own risk and evaluate the results carefully.
# ******************************************************************************************************

import os
from IPython.display import Javascript, display

import shutil
import numpy as np

import os
import random
import time
import threading

try:
    from playsound import playsound

    MUSIC_AVAILABLE = True
except ImportError:
    MUSIC_AVAILABLE = False

import importlib.resources


def SAXS_truncator(input_folder, output_folder, truncation_value=0.251):
    """
    This take the path of a folder containing data not truncated (input folder) and then this will truncate the files to q<0.251.
    This ignores and removes text lines that start with "#", and only keeps the data rows where the first column (q values) is less than the truncation value (default is 0.251).
    and be saved to the path of a folder (the output folder). The new files will be saved with the current naming convention used
    at the Gormley Lab. Ex: a untruncated data file named "Polymer_5_Den_s.dat" will be saved as "Polymer_5_Den_s_SAXS.dat"

    Note:
    If the initial imports for Cesar_SAXS are ran no further imports needed, otherwise import (1) os and (2) pandas as pd
    Parameters:
    ------------
    input_folder: path, str
      The path of the folder containing the files to be truncated, this is passed as a string
    output_folder: path, str
      The path of the folder to store the truncated files, this is passed as a string

    """

    # loop over files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".dat"):
            # open the input file
            with open(os.path.join(input_folder, filename), "r") as f:
                # create a list to hold the rows of data
                data_rows = []
                # loop over lines in the file
                for line in f:
                    # skip any lines that start with "#"
                    if not line.startswith("#"):
                        # split the line into three columns
                        columns = line.strip().split()
                        # check if the second column is less than 0.251
                        if float(columns[0]) < truncation_value:
                            # add the row to the list of data rows
                            data_rows.append(line)
            # create the output file
            with open(
                os.path.join(
                    output_folder,
                    filename.split(".")[0] + "_SAXS." + filename.split(".")[1],
                ),
                "w",
            ) as f:
                # write the data rows to the output file
                for row in data_rows:
                    f.write(row)


def merge_dicts(*dicts):
    """
    Merges any number of dictionaries. If keys overlap, the last one passed takes precedence.
    Useful for combining dictionaries in an analysis folder, where you might have
    multiple dictionaries with the same keys or ran execution on multiple instances.
    Parameters:
    -----------
    *dicts : dict
        Any number of dictionaries to merge.
    """
    merged = {}
    for d in dicts:
        if isinstance(d, dict):
            merged.update(d)
        else:
            raise TypeError(f"Expected dict, got {type(d)}")
    return merged


def check_files_in_directory(file_series, directory):
    """
    Check if files listed in a pandas Series are present in a specified directory.
    Parameters:
    -----------
    file_series : pd.Series
        A pandas Series containing file names to check. If not given series needs to be a list aka put in []
    directory : str
        The path to the directory where the files should be checked.
    """

    # List all files in the given directory
    directory_files = set(os.listdir(directory))

    # Initialize an empty list to store missing files
    missing_files = []

    # Iterate over each file name in the pandas Series
    for file_name in file_series:
        if file_name not in directory_files:
            missing_files.append(file_name)

    # Print missing files, if any
    if missing_files:
        print("Missing files:", str(len(missing_files)))
        for missing_file in missing_files:
            print(missing_file)
    else:
        print("All files are present.")


def copy_files(file_list, source_dir, destination_dir):
    """
    Copies specified files from the source directory to a new destination directory.
    Used for checking files code did bad on

    Parameters:
    -----------
    - file_list: List of file names to be copied.
    - source_dir: Directory where the original files are stored.
    - destination_dir: Directory where the files will be copied.

    The function ensures that the original files are not modified.
    """

    # Ensure destination directory exists
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)  # Create the directory if it doesn’t exist
        print(f"Created destination directory: {destination_dir}")

    # Copy each file
    for file_name in file_list:
        source_path = os.path.join(source_dir, file_name)
        dest_path = os.path.join(destination_dir, file_name)

        if os.path.exists(source_path):  # Check if the file exists before copying
            shutil.copy2(source_path, dest_path)  # Copy with metadata preserved
            print(f"Copied: {file_name} → {destination_dir}")
        else:
            print(f"⚠️ Warning: {file_name} not found in {source_dir}")

    print("Copy process completed!")


def beep():
    """
    Used for notifications
    """
    display(
        Javascript("""
      (async () => {
          const context = new AudioContext();
          const o = context.createOscillator();
          const g = context.createGain();
          o.type = "sine";
          o.connect(g);
          g.connect(context.destination);
          o.start();
          g.gain.exponentialRampToValueAtTime(0.00001, context.currentTime + 1);
      })();
  """)
    )


def get_R2(true_y, fitted_y):
    """
    Gets the fit R^2 value using the formula
    R^2 = 1 - (Sum of squares of residuals / Total sum of squares)

    Parameters
    ----------
    true_y: array
      An array/ series of the original depended variable data
    fitted_y: array
      An array/ series of the fitted dependent variable
    """
    residuals = true_y - fitted_y
    sum_res = np.sum(residuals**2)
    squares_sum = np.sum((true_y - np.mean(true_y)) ** 2)
    return 1 - (sum_res / squares_sum)


def reprocess_sasbdb_q_values(sasbdb_q, sasbdb_I, sasbdb_error):
    """
    Reprocess SASBDB q-values to match lab q-spacing.
    This function is applied to all data used in SAXS Assistant to ensure consistency in q-values.
    It selects q-values from SASBDB/Other data that fall within the range of q-values used in your lab.
    Originally, made to process data from the SASBDB, but can be used for any dataset with q-values.
    It finds the closest q-values from SASBDB to the lab q-values, avoiding duplicates.

    Parameters:
        sasbdb_q (numpy array): q-values from SASBDB.
        sasbdb_I (numpy array): Intensity values from SASBDB.
        sasbdb_error (numpy array or None): Error values from SASBDB (can be None).
        lab_q_array (numpy array): q-values used in your lab.

    Returns:
        dict: Dictionary with selected q, I(q), and errors (if available).
    """
    lab_q_array = np.array(
        [
            0.005,
            0.006,
            0.007,
            0.008,
            0.009,
            0.01,
            0.011,
            0.012,
            0.013,
            0.014,
            0.015,
            0.016,
            0.017,
            0.018,
            0.019,
            0.02,
            0.021,
            0.022,
            0.023,
            0.024,
            0.025,
            0.026,
            0.027,
            0.028,
            0.029,
            0.03,
            0.031,
            0.032,
            0.033,
            0.034,
            0.035,
            0.036,
            0.037,
            0.038,
            0.039,
            0.04,
            0.041,
            0.042,
            0.043,
            0.044,
            0.045,
            0.046,
            0.047,
            0.048,
            0.049,
            0.05,
            0.052,
            0.054,
            0.056,
            0.058,
            0.06,
            0.062,
            0.064,
            0.066,
            0.068,
            0.07,
            0.072,
            0.074,
            0.076,
            0.078,
            0.08,
            0.082,
            0.084,
            0.086,
            0.088,
            0.09,
            0.092,
            0.094,
            0.096,
            0.098,
            0.1,
            0.105,
            0.11,
            0.115,
            0.12,
            0.125,
            0.13,
            0.135,
            0.14,
            0.145,
            0.15,
            0.155,
            0.16,
            0.165,
            0.17,
            0.175,
            0.18,
            0.185,
            0.19,
            0.195,
            0.2,
            0.205,
            0.21,
            0.215,
            0.22,
            0.225,
            0.23,
            0.235,
            0.24,
            0.245,
            0.25,
            0.255,
            0.26,
            0.265,
            0.27,
            0.275,
            0.28,
            0.285,
            0.29,
            0.295,
            0.3,
            0.305,
            0.31,
            0.315,
            0.32,
            0.325,
            0.33,
            0.335,
            0.34,
            0.345,
            0.35,
            0.355,
            0.36,
            0.365,
            0.37,
            0.375,
            0.38,
            0.385,
            0.39,
            0.395,
            0.4,
            0.405,
            0.41,
            0.415,
            0.42,
            0.425,
            0.43,
            0.435,
            0.44,
            0.445,
            0.45,
            0.455,
            0.46,
            0.465,
            0.47,
            0.475,
            0.48,
            0.485,
            0.49,
            0.495,
            0.5,
            0.51,
            0.52,
            0.53,
            0.54,
            0.55,
            0.56,
            0.57,
            0.58,
            0.59,
            0.6,
            0.61,
            0.62,
            0.63,
            0.64,
            0.65,
            0.66,
            0.67,
            0.68,
            0.69,
            0.7,
            0.71,
            0.72,
            0.73,
            0.74,
            0.75,
            0.76,
            0.77,
            0.78,
            0.79,
            0.8,
            0.81,
            0.82,
            0.83,
            0.84,
            0.85,
            0.86,
            0.87,
            0.88,
            0.89,
            0.9,
            0.91,
            0.92,
            0.93,
            0.94,
            0.95,
            0.96,
            0.97,
            0.98,
            0.99,
            1.0,
            1.03,
            1.06,
            1.09,
            1.12,
            1.15,
            1.18,
            1.21,
            1.24,
            1.27,
            1.3,
            1.33,
            1.36,
            1.39,
            1.42,
            1.45,
            1.48,
            1.51,
            1.54,
            1.57,
            1.6,
            1.63,
            1.66,
            1.69,
            1.72,
            1.75,
            1.78,
            1.81,
            1.84,
            1.87,
            1.9,
            1.93,
            1.96,
            1.99,
            2.02,
            2.05,
            2.08,
            2.11,
            2.14,
            2.17,
            2.2,
            2.23,
            2.26,
            2.29,
            2.32,
            2.35,
            2.38,
            2.41,
            2.44,
            2.47,
            2.5,
            2.53,
            2.56,
            2.59,
            2.62,
            2.65,
            2.68,
            2.71,
            2.74,
            2.77,
            2.8,
            2.83,
            2.86,
            2.89,
            2.92,
            2.95,
            2.98,
            3.01,
            3.04,
            3.07,
            3.1,
            3.13,
            3.16,
            3.19,
        ]
    )
    # Step 1: Get min/max q-values from SASBDB
    q_min_sasbdb, q_max_sasbdb = np.min(sasbdb_q), np.max(sasbdb_q)

    # Step 2: Find first and last matching q-values in lab data
    q_min_match = lab_q_array[lab_q_array >= q_min_sasbdb].min()
    q_max_match = lab_q_array[lab_q_array <= q_max_sasbdb].max()

    # Get the q-values from lab that fall within the valid range
    valid_lab_qs = lab_q_array[
        (lab_q_array >= q_min_match) & (lab_q_array <= q_max_match)
    ]

    # Step 3: Find closest q-values from SASBDB to lab q-values
    selected_q, selected_I, selected_error = [], [], []

    for q_target in valid_lab_qs:
        # Get the index of the closest SASBDB q-value to the lab q-value
        idx_closest = np.argmin(np.abs(sasbdb_q - q_target))

        # Avoid duplicate selections
        if selected_q and sasbdb_q[idx_closest] == selected_q[-1]:
            continue  # Skip duplicates

        # Store selected q, I(q), and error (if available)
        selected_q.append(sasbdb_q[idx_closest])
        selected_I.append(sasbdb_I[idx_closest])
        selected_error.append(
            sasbdb_error[idx_closest] if sasbdb_error is not None else None
        )

    # Convert to numpy arrays
    selected_q = np.array(selected_q)
    selected_I = np.array(selected_I)
    selected_error = np.array(selected_error) if sasbdb_error is not None else None

    # Return reprocessed dataset
    return {"q": selected_q, "I": selected_I, "error": selected_error}


def setup_profile_cache():
    helper_alwys = (
        "\x47\x6c\x6f\x72\x79\x20\x74\x6f\x20\x47\x6f\x64\x20\x69\x6e\x20\x74\x68\x65\x20\x68\x69\x67\x68\x65\x73\x74,\x20"
        "\x61\x6e\x64\x20\x6f\x6e\x20\x65\x61\x72\x74\x68\x20\x70\x65\x61\x63\x65\x20\x74\x6f\x20\x70\x65\x6f\x70\x6c\x65\x20"
        "\x6f\x66\x20\x67\x6f\x6f\x64\x20\x77\x69\x6c\x6c\x2e\x20\x57\x65\x20\x70\x72\x61\x69\x73\x65\x20\x79\x6f\x75,\x20"
        "\x77\x65\x20\x62\x6c\x65\x73\x73\x20\x79\x6f\x75,\x20\x77\x65\x20\x61\x64\x6f\x72\x65\x20\x79\x6f\x75,\x20"
        "\x77\x65\x20\x67\x6c\x6f\x72\x69\x66\x79\x20\x79\x6f\x75,\x20\x77\x65\x20\x67\x69\x76\x65\x20\x79\x6f\x75\x20"
        "\x74\x68\x61\x6e\x6b\x73\x20\x66\x6f\x72\x20\x79\x6f\x75\x72\x20\x67\x72\x65\x61\x74\x20\x67\x6c\x6f\x72\x79\x2e\x20"
        "\x4c\x6f\x72\x64\x20\x47\x6f\x64,\x20\x68\x65\x61\x76\x65\x6e\x6c\x79\x20\x4b\x69\x6e\x67,\x20\x4f\x20\x47\x6f\x64,\x20"
        "\x61\x6c\x6d\x69\x67\x68\x74\x79\x20\x46\x61\x74\x68\x65\x72\x2e\x20"
        "\x4c\x6f\x72\x64\x20\x4a\x65\x73\x75\x73\x20\x43\x68\x72\x69\x73\x74,\x20\x4f\x6e\x6c\x79\x20\x42\x65\x67\x6f\x74\x74\x65\x6e\x20\x53\x6f\x6e,\x20"
        "\x4c\x6f\x72\x64\x20\x47\x6f\x64,\x20\x4c\x61\x6d\x62\x20\x6f\x66\x20\x47\x6f\x64,\x20\x53\x6f\x6e\x20\x6f\x66\x20\x74\x68\x65\x20\x46\x61\x74\x68\x65\x72,\x20"
        "\x79\x6f\x75\x20\x74\x61\x6b\x65\x20\x61\x77\x61\x79\x20\x74\x68\x65\x20\x73\x69\x6e\x73\x20\x6f\x66\x20\x74\x68\x65\x20\x77\x6f\x72\x6c\x64,\x20\x68\x61\x76\x65\x20\x6d\x65\x72\x63\x79\x20\x6f\x6e\x20\x75\x73\x3b\x20"
        "\x79\x6f\x75\x20\x74\x61\x6b\x65\x20\x61\x77\x61\x79\x20\x74\x68\x65\x20\x73\x69\x6e\x73\x20\x6f\x66\x20\x74\x68\x65\x20\x77\x6f\x72\x6c\x64,\x20\x72\x65\x63\x65\x69\x76\x65\x20\x6f\x75\x72\x20\x70\x72\x61\x79\x65\x72\x3b\x20"
        "\x79\x6f\x75\x20\x61\x72\x65\x20\x73\x65\x61\x74\x65\x64\x20\x61\x74\x20\x74\x68\x65\x20\x72\x69\x67\x68\x74\x20\x68\x61\x6e\x64\x20\x6f\x66\x20\x74\x68\x65\x20\x46\x61\x74\x68\x65\x72,\x20\x68\x61\x76\x65\x20\x6d\x65\x72\x63\x79\x20\x6f\x6e\x20\x75\x73\x2e\x20"
        "\x46\x6f\x72\x20\x79\x6f\x75\x20\x61\x6c\x6f\x6e\x65\x20\x61\x72\x65\x20\x74\x68\x65\x20\x48\x6f\x6c\x79\x20\x4f\x6e\x65,\x20"
        "\x79\x6f\x75\x20\x61\x6c\x6f\x6e\x65\x20\x61\x72\x65\x20\x74\x68\x65\x20\x4c\x6f\x72\x64,\x20"
        "\x79\x6f\x75\x20\x61\x6c\x6f\x6e\x65\x20\x61\x72\x65\x20\x74\x68\x65\x20\x4d\x6f\x73\x74\x20\x48\x69\x67\x68\x2c\x20\x4a\x65\x73\x75\x73\x20\x43\x68\x72\x69\x73\x74,\x20"
        "\x77\x69\x74\x68\x20\x74\x68\x65\x20\x48\x6f\x6c\x79\x20\x53\x70\x69\x72\x69\x74,\x20\x69\x6e\x20\x74\x68\x65\x20\x67\x6c\x6f\x72\x79\x20\x6f\x66\x20\x47\x6f\x64\x20\x74\x68\x65\x20\x46\x61\x74\x68\x65\x72\x2e\x20\x41\x6d\x65\x6e\x2e"
    )


def clean_path(path_str, resolve_absolute=True):
    """
    Cleans up a path string, fixing Windows-style slashes and removing extra quotes.

    Args:
        path_str (str): The raw path string.
        resolve_absolute (bool): Whether to resolve to absolute path.

    Returns:
        str: Cleaned-up path.
    """
    if not isinstance(path_str, str):
        raise TypeError("Path must be a string.")

    # Strip quotes and whitespace
    path_str = path_str.strip().strip('"').strip("'")

    # Replace backslashes with forward slashes
    cleaned = path_str.replace("\\", "/")

    # Optionally resolve absolute path
    if resolve_absolute:
        cleaned = os.path.abspath(cleaned)

    return cleaned


# utils/helpers.py

# if MUSIC_AVAILABLE:

#     def play_playlist(stop_event, folder="saxs_assistant.music", playlist=None):
#         """

#         Plays a loop of MP3 files from the given package module (e.g., 'saxs_assistant.music')
#         until stop_event is set.
#         """
#         try:
#             # If no specific playlist provided, get all .mp3 files from package folder
#             if playlist is None:
#                 # music_dir = importlib.resources.files("saxs_assistant.music")
#                 music_dir = importlib.resources.files(folder)
#                 playlist = [
#                     file for file in music_dir.iterdir() if file.name.endswith(".mp3")
#                 ]
#                 playlist.sort(key=lambda f: f.name)

#             # Loop through playlist until stop_event is set
#             while not stop_event.is_set():
#                 for track_path in playlist:
#                     if stop_event.is_set():
#                         break
#                     playsound(str(track_path))
#                     time.sleep(0.5)

#         except Exception as e:
#             print(f"⚠️ Music playback error: {e}")
