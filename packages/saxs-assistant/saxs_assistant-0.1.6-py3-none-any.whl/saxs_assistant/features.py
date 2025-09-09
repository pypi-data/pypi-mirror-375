"""This module contains general tools for working with SAXS data with the SAXS Assistant.
This includes dimensionless GPA calculations, and other general tools."""


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
import matplotlib.pyplot as plt


def get_dim_GPA(I, q, rg, i0, plot=False):
    """Calculates the dimensionless GPA (Guinier Peak Analysis) from the given intensity and q values.
    Parameters
    ----------
    I : numpy.ndarray
        Intensity values.
    q : numpy.ndarray
        Scattering vector values.
    rg : float
        Radius of gyration.
    i0 : float
        Intensity at zero angle (I0).
    plot : bool, optional
        If True, plots the data and fit. Default is False.
    Returns
    -------
    x_maxs : numpy.ndarray
        x values of the maxima in the dimensionless GPA plot.
    y_maxs : numpy.ndarray
        y values of the maxima in the dimensionless GPA plot.
    """
    y = (q * rg * I) / i0
    x = (q * rg) ** 2
    index_max_plot = np.argmin(abs(x - 4))

    x_mins, x_maxs, y_mins, y_maxs = min_max_function(
        y[:index_max_plot], x[:index_max_plot]
    )

    if plot:
        plt.plot(x, y, "o", label="Data")
        try:
            plt.plot(x_maxs, y_maxs, "ro", label="Maxs")
        except (ValueError, TypeError):
            plt.title("Dim GPA  ")
            plt.ylabel("qRgI(q)/I(0)")
            plt.xlabel("$(Rgq)^2$")
            plt.xlim([0, 4])
            plt.show()
    return x_maxs, y_maxs


def get_GPA(I, q, plot=False, title=None):
    """
    Computes data for GPA plot (q² vs q·I(q)) in the region q² < 0.0012.

    Parameters:
        I (np.array): Scattering intensity values
        q (np.array): Scattering vector
        plot (bool): If True, returns a matplotlib figure
        title (str): Optional plot title

    Returns:
        If plot=False:
            dict with "x" (q²), "y" (q·I(q)), and "peak_index"
        If plot=True:
            tuple (figure, {"x": ..., "y": ..., "peak_index": ...})
    """
    q_sqr = q * q
    mask = q_sqr < 0.0012  # Setting
    q_sqr = q_sqr[mask]

    i_x_q = q * I
    i_x_q = i_x_q[: len(q_sqr)]  # Match array length
    index_max_y = np.argmax(i_x_q)

    gpa_data = {"x": q_sqr, "y": i_x_q, "peak_index": index_max_y}

    if plot:
        fig, ax = plt.subplots()
        ax.plot(q_sqr, i_x_q, "o")
        ax.set_title(title if title else "GPA Plot")
        ax.axvline(x=q_sqr[index_max_y], color="r", linestyle="--", label="Peak")
        ax.set_ylabel("q·I(q)")
        ax.set_xlabel("$q^2$")
        plt.close(fig)
        return fig, gpa_data

    return gpa_data


def min_max_function(intensity, scatter_angle):
    """
    Finds local minima and maxima in an intensity array. This function
    is used for Method 1 to determine the minima and maxima of the
    residuals of the Guinier fit. Then later applied to try to figure out how
    often the residuals cross the zero line. This is used to try to get an idea
    of biased residuals.
    Parameters:
        intensity: 1D array of intensity values
        scatter_angle: 1D array of scattering angle values corresponding to the intensity
    Returns:
        x_mins, x_maxs: q-values at minima and maxima
        y_mins, y_maxs: intensity values at minima and maxima
    """
    intensity = np.array(intensity)
    scatter_angle = np.array(scatter_angle)

    index_minima, y_mins = [], []
    index_maxima, y_maxs = [], []

    for i in range(1, len(intensity) - 1):
        left, center, right = intensity[i - 1], intensity[i], intensity[i + 1]
        if center < left and center < right:
            index_minima.append(i)
            y_mins.append(center)
        if center > left and center > right:
            index_maxima.append(i)
            y_maxs.append(center)

    if not index_minima and not index_maxima:
        return None, None, None, None

    x_mins = [scatter_angle[i] for i in index_minima]
    x_maxs = [scatter_angle[i] for i in index_maxima]

    return np.array(x_mins), np.array(x_maxs), y_mins, y_maxs


def get_kratky(q, I, plot=False, title=None):
    """
    Computes Kratky plot data (q vs q²I(q)).

    Parameters:
        q (np.array): Scattering vector.
        I (np.array): Intensity values.
        plot (bool): Whether to return a matplotlib figure.
        title (str): Title for the plot.

    Returns:
        If plot=False:
            dict with "x" and "y" data
        If plot=True:
            tuple (figure, {"x": ..., "y": ...})
    """
    Iq_2 = I * (q * q)
    kratky_data = {"x": q, "y": Iq_2}

    if plot:
        fig, ax = plt.subplots()
        ax.plot(q, Iq_2, "o")
        ax.set_xlabel("q")
        ax.set_ylabel(r"$q^2 I(q)$")
        if title:
            ax.set_title(title)
        plt.close(fig)
        return fig, kratky_data

    return kratky_data
