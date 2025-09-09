"""
This module provides tools for working with PDDF (Pair Distribution Function) data and selection.
This includes functions to characterize the data like the Elongation ratio from Putnam 2016
"""

import pandas as pd
from scipy.integrate import trapezoid
import numpy as np
import warnings
import logging
import json
from .rawutils import rawapitry as raw

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


def get_ER(p, r):
    """
    Calculate the Elongation Ratio (ER) from a PDDF.
    If available, some returned values from BIFT cause issues with the
    calculation of the ER, so if this is the case, this isn't calculated.
    Parameters
      ----------
      p : numpy.ndarray
        The PDDF values, P(r)
      r : numpy.ndarray
        The distance values, r
    """
    pr_peak = pd.Series(p, name="P(r)").idxmax()
    P_r = pd.DataFrame({"r": r, "P(r)": p})

    r_spacing = []
    last_r = 0
    current_r = 0
    for j in range(len(P_r["r"])):
        current_r = P_r["r"][j]
        r_spacing.append(current_r - last_r)

        last_r = current_r
    r_spacing = pd.Series(r_spacing, name="delta r")
    P_r = pd.concat([P_r, r_spacing], axis=1)

    zero_R = trapezoid(
        P_r["P(r)"][: pr_peak + 1],
        x=P_r["r"][: pr_peak + 1],
        dx=P_r["delta r"][1],
        axis=-1,
    )
    R_dmax = trapezoid(
        P_r["P(r)"][pr_peak:], x=P_r["r"][pr_peak:], dx=P_r["delta r"][1], axis=-1
    )
    ER = R_dmax / zero_R
    return ER


def unpack_pr_fits_dict(pr_fits_dict):
    """
    Unpacks a pr_fits_dict into the separate lists needed for ranking.
    Returns:
        rg_min, i0_p_list, chi_sq_list, dmax_mins, logas, dmax_err, pr_list,
        pr_i_orig, pr_fit, pr_err_orig, pr_q_orig, pr_qxt, nmins
    """
    rg_min, i0_p_list, chi_sq_list, dmax_mins = [], [], [], []
    logas, dmax_err = [], []
    pr_rg_err, pr_i0_err, pr_qmin, pr_qmax = [], [], [], []
    pr_list, pr_i_orig, pr_fit, pr_err_orig, pr_q_orig, pr_qxt, nmins = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )

    for nmin, fit in pr_fits_dict.items():
        try:
            rg_min.append(fit["Rg"])
            pr_rg_err.append(fit.get("Rg Err", np.nan))  # New
            i0_p_list.append(fit["I0"])
            pr_i0_err.append(fit.get("I0 Err", np.nan))  # New
            chi_sq_list.append(fit["Chi^2"])
            dmax_mins.append(fit["Dmax"])
            logas.append(fit.get("Log Alpha", 0))
            dmax_err.append(fit.get("Dmax Error", 0))
            pr_qmin.append(fit.get("qmin", np.nan))  # New
            pr_qmax.append(fit.get("qmax", np.nan))  # New
            pr_list.append(fit["p(r)"])
            pr_i_orig.append(fit["i_orig"])
            pr_fit.append(fit["i_fit"])
            pr_err_orig.append(fit["err_orig"])
            pr_q_orig.append(fit["q_orig"])
            pr_qxt.append(fit.get("q_extrap", fit["q_orig"]))
            nmins.append(nmin)
        except KeyError as e:
            logging.warning(f"Missing key in pr_fits_dict[{nmin}]: {e}")
            continue

    return (
        rg_min,
        pr_rg_err,
        i0_p_list,
        pr_i0_err,
        chi_sq_list,
        dmax_mins,
        logas,
        dmax_err,
        pr_qmin,
        pr_qmax,
        pr_list,
        pr_i_orig,
        pr_fit,
        pr_err_orig,
        pr_q_orig,
        pr_qxt,
        nmins,
    )


def get_all_pr_results(profile, q, I, err):
    """
    Runs raw.bift at different nmin values and stores the full results for later evaluation.
    #Here maybe dont need to send q, I, err
    """
    pr_fits = {}
    for nmin in range(0, 26, 5):
        # print(f"Running P(r) at nmin = {nmin}"+ "q = "+str(q[nmin]))
        try:
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            (
                gi_bift,
                gi_bift_dmax,
                gi_bift_rg,
                gi_bift_i0,
                gi_bift_dmax_err,
                gi_bift_rg_err,
                gi_bift_i0_err,
                gi_bift_chi_sq,
                gi_bift_log_alpha,
                gi_bift_log_alpha_err,
                gi_bift_evidence,
                gi_bift_evidence_err,
            ) = raw.bift(profile, idx_min=nmin, pr_pts=100, use_guinier_start=False)

            try:
                er = get_ER(gi_bift.p, gi_bift.r)
            except:
                er = None

            pr_fits[nmin] = {
                "Rg": gi_bift_rg,
                "Rg Err": gi_bift_rg_err,
                "I0 Err": gi_bift_i0_err,
                "I0": gi_bift_i0,
                "Dmax": gi_bift_dmax,
                "Chi^2": gi_bift_chi_sq,
                "Log Alpha": gi_bift_log_alpha,
                "Dmax Error": gi_bift_dmax_err,
                "ER": er,
                "q_orig": gi_bift.q_orig,
                "q_extrap": gi_bift.q_extrap,
                "qmin": np.min(gi_bift.q_orig),
                "qmax": np.max(gi_bift.q_orig),
                "i_fit": gi_bift.i_fit,
                "i_orig": gi_bift.i_orig,
                "err_orig": gi_bift.err_orig,
                "p(r)": (gi_bift.r, gi_bift.p),
            }
        except AttributeError:
            # logging.warning(
            #     f"P(r) AttributeError at nmin = {nmin} for {df_wrong['file name'][j]}"
            # )
            pass
        except Exception as e:
            pass
            # logging.warning(
            #     f"P(r) failed at nmin = {nmin} for {df_wrong['file name'][j]}: {e}"
            # )
    return pr_fits


def select_best_pr_fit(
    pr_rg_list,
    pr_rg_err_list,
    pr_i0_list,
    pr_i0_err_list,
    chi_sq_list,
    dmax_list,
    log_alpha_list,
    dmax_err_list,
    pr_qmin_list,
    pr_qmax_list,  #
    final_guinier_rg,
    final_guinier_i0,
    pr_list,
    pr_i_orig,
    pr_fit,
    pr_err_orig,
    pr_q_orig,
    pr_qxt,
    nmins,
    q,
    I,
    err,
    sample_id,
    murthy_df,
    j,
):
    """
    V2. Selects the best P(r) curve whose Rg is within 15% of the final Guinier Rg.
    Updates murthy_df and plot_data with selected P(r). Prioritizes the Rg similarity, followed by Chi distance to 1,
    then the Dmax error, and then the Log Alpha, the candidate Pr at the top of dataframe is returned.
    """
    import numpy as np

    def abs_percent_error(a, b):
        return abs(a - b) / b * 100

    try:
        # Identify indices of candidate P(r) fits within 15% of Guinier Rg
        rg_diffs = [abs_percent_error(final_guinier_rg, rg) for rg in pr_rg_list]
        candidate_inds = np.argwhere(np.array(rg_diffs) < 15).flatten()

        if len(candidate_inds) == 0:
            murthy_df.loc[murthy_df.index[j], "Flag"] = "No PR match to Rg"
            logging.warning(f"No valid P(r) match for {sample_id}")
            return None

        # Build candidate dataframe
        rows = []
        for i in candidate_inds:
            rows.append(
                [
                    i,
                    dmax_list[i],
                    round(chi_sq_list[i], 3),
                    round(log_alpha_list[i], 2),
                    round(dmax_err_list[i], 3),
                    pr_i0_list[i],
                    final_guinier_i0,
                    pr_rg_list[i],
                    final_guinier_rg,
                    abs(
                        1 - round(chi_sq_list[i], 3),
                    ),
                    abs(pr_rg_list[i] - final_guinier_rg),
                ]
            )
        fin_pr = pd.DataFrame(
            rows,
            columns=[
                "Index",
                "Dmax",
                "Chi^2",
                "Log alpha",
                "Dmax Error",
                "Pr i0",
                "G i0",
                "Pr Rg",
                "G Rg",
                "chi dist",
                "Rg Abs dif",
            ],
        )

        # Sort to select best
        # fin_pr = fin_pr.sort_values(by=['chi dist', 'Dmax Error', 'Log alpha'], ascending=[True, True, False]).reset_index(drop=True)
        fin_pr = fin_pr.sort_values(
            by=["Rg Abs dif", "chi dist", "Dmax Error", "Log alpha"],
            ascending=[True, True, True, False],
        ).reset_index(drop=True)

        # display(fin_pr)
        best_idx = int(fin_pr["Index"][0])

        # Update dataframe
        murthy_df.loc[murthy_df.index[j], "Dmax"] = round(dmax_list[best_idx], 4)
        murthy_df.loc[murthy_df.index[j], "Chi^2"] = round(chi_sq_list[best_idx], 4)
        murthy_df.loc[murthy_df.index[j], "Dmax Error RAW"] = round(
            fin_pr["Dmax Error"][0], 4
        )
        murthy_df.loc[murthy_df.index[j], "Pr Rg"] = round(pr_rg_list[best_idx], 4)
        murthy_df.loc[murthy_df.index[j], "Pr i0"] = pr_i0_list[best_idx]
        murthy_df.loc[murthy_df.index[j], "Pr Log Alpha"] = log_alpha_list[best_idx]
        murthy_df.loc[murthy_df.index[j], "Pr nmin"] = round(nmins[best_idx], 4)
        murthy_df.loc[murthy_df.index[j], "Pr Rg Err"] = round(
            pr_rg_err_list[best_idx], 4
        )
        murthy_df.loc[murthy_df.index[j], "Pr i0 Err"] = round(
            pr_i0_err_list[best_idx], 4
        )
        murthy_df.loc[murthy_df.index[j], "Pr qmin"] = round(pr_qmin_list[best_idx], 4)
        murthy_df.loc[murthy_df.index[j], "Pr qmax"] = round(pr_qmax_list[best_idx], 4)
        return fin_pr, best_idx

    except Exception as e:
        logging.warning(f"Error selecting final P(r) for {sample_id}: {e}")
        murthy_df.loc[murthy_df.index[j], "Flag"] = "PR selection error"
        return None


# Functions to help correct when script chooses wrong PDDF from Raw
def extract_gnom_parameters(file_path):
    """
    This extracts the Rg, Rg error, I0, I0 error and Dmax from a .out file from GNOM
    The name of the file should match exactly what the profile of what was given to SAXS_Assistant was
    only the extension should be different

    """

    # Read first ~150 lines (or more if needed) from the GNOM file
    df = pd.read_csv(
        file_path,
        sep=r"\s+",
        engine="python",
        nrows=150,
        usecols=range(6),  # Capture first 6 columns
        header=None,  # No header row
    )

    rg, i0, dmax = None, None, None

    for i in range(len(df)):
        row = df.iloc[i].astype(str)

        if "Rg:" in row.values:
            rg_idx = row[row == "Rg:"].index[0] + 1
            rg_err_idx = row[row == "Rg:"].index[0] + 3
            rg = pd.to_numeric(row[rg_idx], errors="coerce")
            rg_err = pd.to_numeric(row[rg_err_idx], errors="coerce")

        if "I(0):" in row.values:
            i0_idx = row[row == "I(0):"].index[0] + 1
            i0_err_idx = row[row == "I(0):"].index[0] + 3
            i0 = pd.to_numeric(row[i0_idx], errors="coerce")
            i0_err = pd.to_numeric(row[i0_err_idx], errors="coerce")

        if "range:" in row.values:
            dmax_idx = row[row == "range:"].index[0] + 3
            dmax = pd.to_numeric(row[dmax_idx], errors="coerce")

    return rg, rg_err, i0, i0_err, dmax


def extract_pr_data_gnom(gnom_path):  # works this just extracts pddf
    """
    Extracts P(r) data from a GNOM .out file.

    Parameters:
    - gnom_path (str or Path): Path to the .out file generated by GNOM.

    Returns:
    - pd.DataFrame: DataFrame with columns ['R', 'P(R)', 'ERROR']
    """
    with open(gnom_path, "r") as f:
        lines = f.readlines()

    # Find the line that starts with "R   P(R)   ERROR"
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("R") and "P(R)" in line and "ERROR" in line:
            start_idx = i
            break

    if start_idx is None:
        raise ValueError("Could not find P(r) data header in GNOM file.")

    # Read the file from that line onward using pandas
    pr_df = pd.read_csv(gnom_path, sep=r"\s+", skiprows=start_idx, engine="python")

    return pr_df


def extract_saxs_from_gnom(file_path):
    """
    Extracts experimental SAXS and P(r) data from a GNOM .out file.

    Parameters:
        file_path (str): Path to GNOM .out file.

    Returns:
        pr_df (pd.DataFrame): DataFrame with columns ['R', 'P(R)', 'ERROR'].
        exp_fit_df (pd.DataFrame): DataFrame with columns like ['q', 'I_exp', 'Error', 'I_fit'] (if available).
        reduced_chi_squared(float): value of chi squared w 1 deg freedom
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    pr_start = None
    exp_fit_start = None

    # Find P(r) section this one is always at the bottom of the file
    for i, line in enumerate(lines):
        if line.strip().startswith("R") and "P(R)" in line and "ERROR" in line:
            pr_start = i
            break

    if pr_start is None:
        raise ValueError("Could not find P(r) data header in GNOM file.")

    # Find Experimental Fit section by scanning upward from P(r)
    for j in range(pr_start, 0, -1):
        if "Experimental" in lines[j] and "Fit" in lines[j]:
            exp_fit_start = j + 1  # actual data starts one line after
            break

    if exp_fit_start is None:
        raise ValueError("Could not find Experimental Fit section in GNOM file.")

    # Load P(r)
    pr_df = pd.read_csv(file_path, sep=r"\s+", skiprows=pr_start, engine="python")

    # Load experimental + fit data (up to pr_start - 1)
    exp_fit_df = pd.read_csv(
        file_path,
        sep=r"\s+",
        skiprows=exp_fit_start,
        nrows=pr_start - exp_fit_start,
        engine="python",
    )
    exp_fit_df = exp_fit_df.iloc[
        :, :5
    ]  # some reason the colum name of the last two gets read as 2 diff cols

    # Opnly need the first five columns
    expected_cols = ["q_extr", "I_fit", "I_error", "J_reg", "I_reg"]
    exp_fit_df = exp_fit_df.iloc[:, : len(expected_cols)]
    exp_fit_df.columns = expected_cols
    # Making it numeric
    exp_fit_df["q_extr"] = pd.to_numeric(exp_fit_df["q_extr"], errors="coerce")

    # Here figuring out what columns should be dropped and using q for this bc q cant be negative
    # So this would result in the empty or non numeric to be nan then we drop everything below the first index that meets that including itself

    # Find the first bad index or first false
    print(exp_fit_df["q_extr"] > -1)
    bad_index = exp_fit_df[~(exp_fit_df["q_extr"] > -1)].index.min()

    # If such a row exists, trim the dataframe w everything below it
    if pd.notna(bad_index):
        exp_fit_df = exp_fit_df.iloc[:bad_index].reset_index(drop=True)
    exp_fit_df["I_error"] = pd.to_numeric(exp_fit_df["I_error"], errors="coerce")
    exp_fit_df["I_fit"] = pd.to_numeric(exp_fit_df["I_fit"], errors="coerce")
    exp_fit_df["I_reg"] = pd.to_numeric(exp_fit_df["I_reg"], errors="coerce")
    exp_fit_df["J_reg"] = pd.to_numeric(exp_fit_df["J_reg"], errors="coerce")

    # Last now just need to get the Chi Squared from them, easier to calculate it
    # They use the fit instead of experimental for the residuals plot
    valid = exp_fit_df[exp_fit_df["I_reg"].notna()]  # This where I isnt empty

    residuals_pr = (valid["I_fit"] - valid["I_reg"]) / valid["I_error"]

    # Compute chi-squared
    residuals_squared = ((valid["I_reg"] - valid["I_fit"]) / valid["I_error"]) ** 2
    chi_squared = np.sum(residuals_squared)

    # Degrees of freedom
    N = len(valid)
    p = 1  # Tested w files they use 1
    reduced_chi_squared = chi_squared / (N - p)

    return pr_df, exp_fit_df, residuals_pr, reduced_chi_squared


# This is for gettin  BIFT .ift Data


def read_bift_ift_file(file_path):
    """
    Reads a BIFT .ift file and returns two DataFrames:
    1. pr_df: the P(R) curve from start to second occurrence of P(R) == 0.
    2. fit_df: the I(Q), Error, and Fit values up to 'Q_extrap' marker.
    """

    try:
        # --------- Read P(R) Section ---------
        pr_df = pd.read_csv(
            file_path,
            sep=r"\s+",
            engine="python",
            skiprows=2,  # Skip '# BIFT' and '# R P(R) Error'
            names=["R", "P(R)", "Error"],
            on_bad_lines="skip",
        )
        pr_df["P(R)"] = pd.to_numeric(pr_df["P(R)"], errors="coerce")

        # Find where P(R) ends (2nd zero)
        possible_ends = pr_df[pr_df["P(R)"] == 0].index
        if len(possible_ends) >= 2:
            end_idx = possible_ends[1]
            pr_df = pr_df.iloc[: end_idx + 1]
            # display(pr_df)
        else:
            print(
                f"Warning: Less than two P(R)=0 found in {file_path}; using full curve."
            )
            end_idx = pr_df.index[-1]  # fallback

        pr_df = pr_df.reset_index(drop=True)

        # --------- Read Fit Section ---------
        fit_start = end_idx + 6
        df = pd.read_csv(
            file_path,
            sep=r"\s+",
            engine="python",
            skiprows=fit_start,
            header=None,
            names=["Q", "I(Q)", "Error", "Fit"],
            on_bad_lines="skip",
        )

        # Cut off before extrapolated section
        fit_plot_end = df[
            df.apply(lambda row: row.astype(str).str.contains("Q_extrap").any(), axis=1)
        ].index[0]
        fit_df = df.iloc[:fit_plot_end].copy()

        # Convert to numeric
        for col in ["Q", "I(Q)", "Error", "Fit"]:
            fit_df[col] = pd.to_numeric(fit_df[col], errors="coerce")

        return pr_df, fit_df

    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
        return None, None


def read_bift_metadata(file_path):
    """
    The bottom that has the parameters is in JSON style so this reads it. I dont extract the actual fully extrapolated bc not even used for plotting


    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Find JSON block at the end (starts with '#{' and ends with '#}')
    start_idx, end_idx = None, None
    for i in reversed(range(len(lines))):
        if lines[i].strip() == "#}":
            end_idx = i
        elif lines[i].strip() == "#{":
            start_idx = i
            break

    if start_idx is not None and end_idx is not None:
        # Extract and clean lines
        json_lines = lines[start_idx + 1 : end_idx]
        json_str = "".join(line.lstrip("#").strip() for line in json_lines)
        metadata = json.loads("{" + json_str + "}")

        # Extract desired values
        keys_of_interest = [
            "dmax",
            "i0",
            "qmax",
            "qmin",
            "rg",
            "rger",
            "dmaxer",
            "chisq",
            "alpha",
        ]
        return {k: metadata[k] for k in keys_of_interest if k in metadata}

    return None  # Or raise an error if you want
