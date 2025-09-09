# ******************************************************************************
# This file is part of SAXS Assistant.
#
#
#    If you use this code in your work, please cite the following publications:
# Hansen, S. Journal of Applied Crystallography (2000) 33, 1415-1421. DOI: 10.1107/S0021889800012930

# https://doi.org/10.1107/S1600576723011019
# https://doi.org/10.1107/S0021889809023863
# https://doi.org/10.1016/j.bpj.2018.04.018

#    SAXS Assistant is based on the code from RAW, which is a SAXS data analysis software.
#
#
#    SAXS Assistant utilizes parts of the code from RAW
#    SAXS Assistant is shared for helping the community with SAXS data analysis.
#    but it is not a replacement for RAW, and does not include all the features of RAW.
#    SAXS Assisant does not offer warranty-- use at your own risk and evaluate the results carefully.
# ******************************************************************************************************


import os
import pandas as pd
import joblib
import shutil
from typing import Optional
from natsort import natsorted
from pathlib import Path


def combine_sessions(base_path: str, output_name: str = "final_results"):
    """
    Combines results from multiple concurrent SAXS analysis runs stored in folders like
    'return', 'return_1', 'return_2', etc., within a given base path.

    Parameters:
        base_path (str): Path where the return folders are located.
        output_name (str): Base name for the final output files (Excel and joblib).
    """

    return_dirs = [d for d in os.listdir(base_path) if d.startswith("return")]
    sorted_dirs = natsorted(return_dirs)

    combined_df = pd.DataFrame()
    combined_dict = {}
    seen_files = set()
    i = 0  # counter to append dfs in order
    for dir_name in sorted_dirs:
        folder_path = os.path.join(base_path, dir_name)
        results_path = os.path.join(folder_path, "results.xlsx")
        dict_path = os.path.join(folder_path, "plot_data.joblib")

        # Read and combine dataframe
        if os.path.exists(results_path):
            df = pd.read_excel(results_path)
            # If not the first folder, drop any already seen 'file name' rows
            if i > 0 and "file name" in df.columns:
                df = df[~df["file name"].isin(seen_files)]

            # Tracking new file names probs dont need but better safe
            if "file name" in df.columns:
                seen_files.update(df["file name"].dropna().unique())

            combined_df = pd.concat([combined_df, df], ignore_index=True)

        # Read and combine dictionary
        if os.path.exists(dict_path):
            temp_dict = joblib.load(dict_path)
            combined_dict.update(temp_dict)
        i += 1
    # Save combined results
    combined_df.to_excel(os.path.join(base_path, f"{output_name}.xlsx"), index=False)
    joblib.dump(combined_dict, os.path.join(base_path, f"{output_name}_Plots.joblib"))

    # Move return folders to a subdirectory
    partials_path = os.path.join(base_path, "partials")
    os.makedirs(partials_path, exist_ok=True)

    for dir_name in sorted_dirs:
        shutil.move(
            os.path.join(base_path, dir_name), os.path.join(partials_path, dir_name)
        )

    print(
        f"Combined results saved as '{output_name}.xlsx' and '{output_name}_Plots.joblib' in {base_path}"
    )
    print(f"Original folders moved to '{partials_path}'")


def split_results(df_path):
    """
    Cleans a DataFrame by removing rows with missing 'Pr Rg' or 'Final Rg',
    and rows with non-empty 'Fatal Error' if the column exists.
    Saves two dataframes: 'full_solved.xlsx' and 'flagged.xlsx' in the same directory.
    """
    df_path = Path(df_path)
    if not df_path.exists():
        raise FileNotFoundError(f"File not found: {df_path}")

    print(f"Loading: {df_path}")
    # Load the dataframe (Excel or CSV)
    if df_path.suffix.lower() == ".csv":
        df = pd.read_csv(df_path)
    elif df_path.suffix.lower() in [".xls", ".xlsx"]:
        df = pd.read_excel(df_path)
    else:
        raise ValueError(f"Unsupported file format: {df_path.suffix}")

    # Create masks
    missing_rg_mask = df["Pr Rg"].isna() | df["Final Rg"].isna()

    if "Fatal Error" in df.columns:
        fatal_error_mask = df["Fatal Error"].notna() & df["Fatal Error"].astype(
            str
        ).str.strip().ne("")
    else:
        fatal_error_mask = pd.Series([False] * len(df), index=df.index)

    # Combine conditions
    flagged_mask = missing_rg_mask | fatal_error_mask

    # Split the dataframe
    df_flagged = df[flagged_mask].copy()
    df_full_solved = df[~flagged_mask].copy()

    # Prepare output paths
    out_dir = df_path.parent
    flagged_out = out_dir / "flagged.xlsx"
    solved_out = out_dir / "full_solved.xlsx"

    print(f"Saving solved rows to: {solved_out}")
    df_full_solved.to_excel(solved_out, index=False)

    print(f"Saving flagged rows to: {flagged_out}")
    df_flagged.to_excel(flagged_out, index=False)

    print(
        f"\n✅ Done! {len(df_full_solved)} solved rows, {len(df_flagged)} flagged rows."
    )

    return df_full_solved, df_flagged


def sort_profiles(results_dir):
    """
    Given a directory containing 'full_solved.xlsx' and/or 'flagged.xlsx',
    copies the files listed in the 'file' column of each sheet into separate folders:
    'solved profiles/' and 'flagged profiles/'.

    Parameters:
    -----------
    - results_dir: Path to the directory containing the result Excel sheets.
    """
    results_dir = Path(results_dir)
    if not results_dir.exists() or not results_dir.is_dir():
        raise NotADirectoryError(
            f"Provided path is not a valid directory: {results_dir}"
        )

    excel_files = {
        "full_solved.xlsx": "solved profiles",
        "flagged.xlsx": "flagged profiles",
    }

    for excel_name, profile_folder in excel_files.items():
        excel_path = results_dir / excel_name
        output_dir = results_dir / profile_folder

        if excel_path.exists():
            print(f"\nFound {excel_name}, copying files...")

            # Load the dataframe
            df = pd.read_excel(excel_path)

            # Check for 'file' column
            if "file name" not in df.columns:
                print(
                    f"⚠️ Warning: 'file name' column not found in {excel_name}, skipping."
                )
                continue

            # Make sure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Copy each file
            for idx, row in df.dropna(subset=["file name"]).iterrows():
                file_name = str(row["file name"]).strip()
                file_path = Path(str(row["path"]).strip())
                source_path = file_path / file_name
                dest_path = output_dir / file_name

                if source_path.exists():
                    shutil.copy2(source_path, dest_path)
                    print(f"✔ Copied: {file_name} → {output_dir.name}")
                else:
                    print(f"⚠️ Missing file: {file_name} at {source_path}")

        else:
            print(f"⚠️ {excel_name} not found in {results_dir}, skipping.")

    print("\n✅ Profile copy process complete!")
