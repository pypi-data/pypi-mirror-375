"""This module contains tools for working Rg. Including the determination using the
custom method from script called Method 1, and evaluating guinier fits from both methods, including those
obtained from RAW."""
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

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import logging

# from .utils import helpers
from .utils.helpers import get_R2
from .features import get_dim_GPA

from .features import min_max_function


def get_guinier_from_min_max_2(I, q, error, nmin, nmax, plot=False):
    """
    V2 Computes Guinier fit and associated parameters including Rg, I0, R², and their errors.
    Similarly to BioXTAS but uses the values of Rg obtained from multiple BIFT Pr calculations
    as qmin is truncated to only consider fits within the range of possible Rgs from real space.
    This is used within a loop.
    Parameters
    ----------
    I : numpy.ndarray
        Intensity values.
    q : numpy.ndarray
        Scattering vector values.
    error : numpy.ndarray
        Error values associated with the intensity.
    nmin : int
        Minimum index for the Guinier fit.
    nmax : int
        Maximum index for the Guinier fit.
    plot : bool, optional
        If True, plots the data and fit. Default is False.
    Returns
    -------
    rg : float
        Radius of gyration.
    i0 : float
        Intensity at zero angle (I0).
    fR2 : float
        Coefficient of determination (R²) for the fit.
    guinier_dict : dict
        Dictionary containing various parameters from the Guinier fit.
    ax1, ax1a, ax2, ax2a : matplotlib.axes.Axes
        Axes objects for plotting the data and fit.
    """

    def linearFunc(x, intercept, slope):
        return intercept + slope * x

    end = nmax + 1
    x = np.array(q[nmin:end]) ** 2
    y = np.log(I[nmin:end])
    err = np.abs(error[nmin:end] / I[nmin:end])

    valid = np.isfinite(y)
    x, y, err = x[valid], y[valid], err[valid]

    a_fit, cov = curve_fit(linearFunc, x, y, sigma=err, absolute_sigma=True)
    intercept, slope = a_fit
    yfit = linearFunc(x, intercept, slope)
    fR2 = get_R2(y, yfit)

    # Compute Rg and I0
    rg = np.sqrt(-3 * slope) if slope < 0 else np.nan
    i0 = np.exp(intercept)

    # Error propagation
    try:
        slope_var = cov[1, 1]
        intercept_var = cov[0, 0]
        rg_err = (0.5 / rg) * np.sqrt(3 * slope_var) if slope < 0 else np.nan
        i0_err = i0 * np.sqrt(intercept_var)
    except Exception:
        rg_err = np.nan
        i0_err = np.nan

    # qRg bounds
    qminRg = q[nmin] * rg
    qmaxRg = q[end - 1] * rg
    qmin = q[nmin]
    qmax = q[end - 1]

    # Residual analysis
    residuals = (y - yfit) / err
    x_mins, x_maxs, y_mins, y_maxs = min_max_function(residuals, x)

    # Count x-crossings
    crossed = 0
    strt = residuals[0]
    for ii in range(1, len(residuals)):
        current = residuals[ii]
        if (strt > 0 and current < 0) or (strt < 0 and current > 0):
            crossed += 1
        strt = current

    peaks_v_cross = 0
    try:
        peaks_v_cross = crossed / (len(x_mins) + len(x_maxs))
    except ZeroDivisionError:
        pass

    GPAx_maxs, GPAy_maxs = get_dim_GPA(I, q, rg, i0)
    closest_Gx = GPAx_maxs[np.argmin(abs(GPAx_maxs - 1.5))] if len(GPAx_maxs) > 0 else 0
    closest_Gy = GPAy_maxs[np.argmin(abs(GPAx_maxs - 1.5))] if len(GPAy_maxs) > 0 else 0

    len_res = max(residuals) - min(residuals)

    if plot:
        fig, ax1 = plt.subplots()
        fig, ax1a = plt.subplots()
        ax1.plot(x, y, "o", label="Data")
        ax1a.plot(x, yfit, label="Fit $R^2$ " + str(round(fR2, 4)))

        fig, ax2 = plt.subplots()
        fig, ax2a = plt.subplots()
        ax2.plot(x, residuals, "o")
        try:
            ax2.plot(x_mins, y_mins, "og")
            ax2.plot(x_maxs, y_maxs, "oc")
        except Exception:
            pass
        ax2a.plot(x, np.zeros(len(x)), "r")
    else:
        ax1 = ax1a = ax2 = ax2a = 0

    guinier_dict = {
        "Rg": [rg],
        "Rg Err": [rg_err],
        "i0": [i0],
        "I0 Err": [i0_err],
        "fit_r2": [fR2],
        "qRgmin": [qminRg],
        "qRgmax": [qmaxRg],
        "qmin": [qmin],
        "qmax": [qmax],
        "peaks/x-cross": [peaks_v_cross],
        "GPA x peak": [closest_Gx],
        "GPA y peak": [closest_Gy],
        "Res window": [len_res],
        "nmin": nmin,
        "nmax": nmax,
    }

    return rg, i0, fR2, guinier_dict, ax1, ax1a, ax2, ax2a


def calculate_guinier_Iq(q, rg, i0):
    """
    Returns I(q) calculated from Guinier approximation:
    I(q) = I0 * exp(-Rg^2 * q^2 / 3)
    Used for evaluating the Guinier fit of both methods, based on the
    agreement of the Rg and I0 values obtained from the fit.
    Parameters
    ----------
    q : numpy.ndarray
        Scattering vector values.
    rg : float
        Radius of gyration.
    i0 : float
        Intensity at zero angle (I0).
    Returns
    -------
    numpy.ndarray
        Calculated intensity values I(q) based on the Guinier approximation.
    """
    return i0 * np.exp(-(rg**2 * q**2) / 3)


def rg_method_1(q, I, err, pr_rg_list):
    """
    Performs second-pass Guinier fits using Rg range from P(r).
    Returns best-fit DataFrame and list of all candidate fits.
    """
    # print(pr_rg_list)
    gds = []

    for i in range(30):  # Start indices
        dynamic_bound = int((len(q) - i) - 1)
        for window in range(7, dynamic_bound):
            try:
                rg, i0, r2, gd, *_ = get_guinier_from_min_max_2(
                    I, q, err, i, i + window
                )
            except Exception:
                continue

            qrgmin = rg * q[i]
            qrgmax = rg * q[i + window - 1]

            if rg >= min(pr_rg_list) * 0.91 and rg <= max(pr_rg_list) * 1.09:
                if r2 > 0.74 and qrgmax < 1.4 and qrgmin < 0.9 and qrgmax > 0.9:
                    gds.append(gd)

    if not gds:
        return None, []

    # Collect and return all good fits
    all_gds_df = pd.concat(
        [pd.DataFrame.from_dict(gd) for gd in gds], ignore_index=True
    )
    return all_gds_df, gds


def select_final_rg_from_candidates(gds, q, I, err, sample_id="unknown"):
    """
    From a list of Guinier fits (Method 1), filters and selects the best candidate.
    Returns final Guinier DataFrame or None if unresolved.
    """
    if not gds:
        logging.warning(f"No Guinier fits found for {sample_id}")
        return None

    GD = pd.DataFrame.from_dict(gds[0])
    for gd in gds[1:]:
        GD = pd.concat([GD, pd.DataFrame.from_dict(gd)], axis=0, ignore_index=True)

    filt1 = GD[GD["qRgmin"] <= 0.9]
    # print('filt1')
    # display(filt1)
    if len(filt1["GPA x peak"]) < 1:
        return None

    filt2 = filt1[filt1["qRgmax"] < 1.4]
    if len(filt2) < 1:
        filt2 = filt1[filt1["qRgmax"] < 1.5]

    filt3 = filt2[filt2["peaks/x-cross"] <= 1.33]
    if len(filt3) < 1:
        return None

    filt4 = (
        filt3.copy()
        .sort_values(by=["peaks/x-cross", "qRgmin"], ascending=[False, True])
        .reset_index(drop=True)
    )
    # print('Filt4')
    # display(filt4)
    # Bin Rgs
    filter_df = filt4.round({"Rg": 0, "qRgmin": 2})
    u_rgs = np.sort(filter_df["Rg"].unique())
    if len(u_rgs) < 1:
        return None

    # Generate bin edges (10% increments)
    frst_l = [u_rgs[0]]
    while frst_l[-1] < u_rgs[-1]:
        frst_l.append(round(frst_l[-1] * 1.10) + 1)
    if len(frst_l) < 2:
        frst_l.append(frst_l[-1] + 1)

    # Histogram
    h_vals, bin_edges = np.histogram(filter_df["Rg"], bins=frst_l)
    try:
        most_occur_idx = np.argmax(h_vals)
        rg_lb = bin_edges[most_occur_idx]
        rg_ub = bin_edges[most_occur_idx + 1]
    except Exception:
        logging.warning(f"Histogram selection failed for {sample_id}")
        return None

    f1 = filter_df[(filter_df["Rg"] >= rg_lb) & (filter_df["Rg"] < rg_ub)].sort_values(
        by=["nmin", "nmax"]
    )
    if len(f1) < 1:
        return None

    nmin_new = int(f1["nmin"].min())
    nmax_new = int(f1["nmax"].max())

    # New round of Guinier fitting centered around this Rg window
    new_gds = []
    range_expand = int((nmax_new - nmin_new) * 0.15)
    for i in range(range_expand):
        for jj in range(-range_expand, range_expand):
            try:
                rg, i0, r2, gd, *_ = get_guinier_from_min_max_2(
                    I, q, err, nmin_new + i, nmax_new - jj, plot=False
                )
                if r2 > 0.73:
                    new_gds.append(gd)
            except:
                continue

    if not new_gds:
        return None

    final_df = pd.DataFrame.from_dict(new_gds[0])
    for gd in new_gds[1:]:
        final_df = pd.concat(
            [final_df, pd.DataFrame.from_dict(gd)], axis=0, ignore_index=True
        )

    # Apply quality filters
    filt1 = final_df[final_df["qRgmin"] <= 0.9]
    if len(filt1) < 1:
        # print('returned non lst -1')
        return None

    filt2 = filt1[filt1["qRgmax"] < 1.4]
    if len(filt2) < 1:
        filt2 = filt1[filt1["qRgmax"] < 1.55]

    filt3 = filt2[filt2["peaks/x-cross"] <= 1.33]
    if len(filt3) < 1:
        # print('Returned non last')
        return None

    # Final sort and return
    filt4 = filt3.sort_values(
        by=["peaks/x-cross", "qRgmin"], ascending=[False, True]
    ).reset_index(drop=True)
    # print('-------------------Final ---------------------------------------')
    # display(filt4)
    return filt4


def select_best_rg_method(
    q,
    I,
    err,
    rg_auto,
    i0_auto,
    rg1,
    i01,
    rg_auto_err=None,
    i0_auto_err=None,
    rg1_err=None,
    i01_err=None,
    r2_auto=None,
    r2_1=None,
    nmin_auto=None,
    nmax_auto=None,
    m1_nmin=None,
    m1_nmax=None,
    method1_exists=None,
    sample_id="unknown",
):
    """
    Compares AutoRg and Method 1 fits using residuals and selects the best.
    Returns: final_rg, final_i0, selected_method
    """
    try:
        # Generate Guinier I(q) predictions
        I_fit_auto = calculate_guinier_Iq(q, rg_auto, i0_auto)
        I_fit_1 = calculate_guinier_Iq(q, rg1, i01)

        # Compute residual stats
        res_auto = compute_guinier_residuals_Limited(I, I_fit_auto, err, q, rg_auto)
        res_1 = compute_guinier_residuals_Limited(I, I_fit_1, err, q, rg1)

        mean_auto = res_auto["residual_mean"][0]
        mean_1 = res_1["residual_mean"][0]

        # If Method 1 exists, check if AutoRg quality is acceptable
        # This prevents loosing a good method 1 result when auto did bad as for example for a file had both give similar Rg
        # But auto had R2 ~ 0.3 but bc residuals were better it got chosen but then the file gets marked as unsolved

        # method1_exists = res_1 is not None and "residual_mean" in res_1

        if method1_exists:
            auto_too_few_points = (nmax_auto - nmin_auto + 1) < 7
            auto_low_r2 = r2_auto < 0.73

            if auto_too_few_points or auto_low_r2:
                # Penalize AutoRg to favor Method 1
                mean_auto = res_1["residual_mean"][0] + 999
                # If method 1 doesnt exist and auto has bad r2 or num point outter catches it

        if mean_auto <= mean_1:
            selected = "AutoRg"
            final_rg, final_i0 = rg_auto, i0_auto
            final_rg_err, final_i0_err = rg_auto_err, i0_auto_err
            final_r2 = r2_auto
            final_res = res_auto
            final_qrgmin = rg_auto * min(q)
            final_qrgmax = rg_auto * max(q)
            final_nmin = nmin_auto
            final_nmax = nmax_auto

        else:
            selected = "Method 1"
            final_rg, final_i0 = rg1, i01
            final_rg_err, final_i0_err = rg1_err, i01_err
            final_r2 = r2_1
            final_res = res_1
            final_qrgmin = rg1 * min(q)
            final_qrgmax = rg1 * max(q)
            final_nmin = m1_nmin
            final_nmax = m1_nmax

        return {
            "Final Rg": final_rg,
            "Final I0": final_i0,
            "Final Rg Err": final_rg_err,
            "Final I0 Err": final_i0_err,
            "Final R²": final_r2,
            "Selected Method": selected,
            "Residual Stats": final_res,
            "Final qRg min": final_qrgmin,
            "Final qRg max": final_qrgmax,
            "Final nmin": final_nmin,
            "Final nmax": final_nmax,
        }

    except Exception as e:
        logging.warning(f"Failed to select best Rg method for {sample_id}: {e}")
        return None


def compute_guinier_residuals_Limited(y_exp, y_fit, y_err, q, rg, num_params=1):
    valid_mask = ~np.isnan(y_exp) & ~np.isnan(y_fit)
    # Apply the mask
    qrg = q[valid_mask] * rg
    y_exp = y_exp[valid_mask][qrg <= 2]
    y_fit = y_fit[valid_mask][qrg <= 2]
    y_err = np.array(y_err)[valid_mask][qrg <= 2] if y_err is not None else None
    residuals = y_exp - y_fit

    if y_err is not None:
        chi_squared = np.sum((residuals / y_err) ** 2)
    else:
        chi_squared = np.sum(residuals**2)

    reduced_chi_squared = (
        chi_squared / (len(residuals) - num_params)
        if len(residuals) > num_params
        else np.nan
    )

    return {
        "residual_mean": [np.mean(np.abs(residuals))],
        "residual_median": [np.median(np.abs(residuals))],
        "residual_std": [np.std(residuals)],
        "residual_max": [np.max(np.abs(residuals))],
        "Reduced Chi Squared": [reduced_chi_squared],
        # 'residual_array': residuals
    }


def get_residuals_guinier_plot(I, q, error, nmin, nmax, extra=2):
    def linearFunc(x, intercept, slope):
        return intercept + slope * x

    # nmin_ext = max(0, nmin - extra)
    nmin_ext = 0

    # nmax_ext = min(len(q), nmax + extra + 1)
    nmax_ext = len(q) - 1

    x_fit = np.array(q[nmin : nmax + 1]) ** 2
    y_fit = np.log(I[nmin : nmax + 1])
    err_fit = np.abs(error[nmin : nmax + 1] / I[nmin : nmax + 1])

    valid = np.isfinite(y_fit)
    x_fit, y_fit, err_fit = x_fit[valid], y_fit[valid], err_fit[valid]

    a_fit, cov = curve_fit(linearFunc, x_fit, y_fit, sigma=err_fit, absolute_sigma=True)
    intercept, slope = a_fit
    y_model = linearFunc(x_fit, intercept, slope)

    residuals = (y_fit - y_model) / err_fit
    x_mins, x_maxs, y_mins, y_maxs = min_max_function(residuals, x_fit)

    x_all = np.array(q[nmin_ext:nmax_ext]) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        y_all = np.log(I[nmin_ext:nmax_ext])
    err_all = np.abs(error[nmin_ext:nmax_ext] / I[nmin_ext:nmax_ext])
    valid = np.isfinite(y_all)
    x_all, y_all, err_all = x_all[valid], y_all[valid], err_all[valid]

    return {
        "x_all": x_all,  # This all the q**2 values that passed mask
        "y_all": y_all,  # All Ln(i(q)) that arent nan
        "x_fit": x_fit,  # The actual X_values of the fit (q**2)
        "y_fit": y_fit,  # The actual Ln(I(q)) values NOT the fit but the data used for it
        "residuals": residuals,  # The resdiauls in the fit
        "x_mins": x_mins,  # This if want to plot the mins and max
        "x_maxs": x_maxs,
        "y_mins": y_mins,
        "y_maxs": y_maxs,
        "nmin_ext": nmin_ext,  # This is always just the first q value
        "nmax_ext": nmax_ext,  # Always the last q value
        "y_model": y_model,  # This is the actual fit model, the straight line
        "Rg": (-3 * slope) ** (1 / 2),
        "i0": intercept,
    }
