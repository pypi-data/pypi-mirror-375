import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter
import numpy as np
from ..features import min_max_function
from ..rg_tools import get_residuals_guinier_plot
import pandas as pd

# from .utils.helpers import clean_path
from joblib import load


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


def plot_solved_summary(
    plot_data_path, output_folder=None, pdf_name="solved_summary.pdf"
):
    """
    Plots the solved data files. If an output folder is not provided,
    saves to the same folder where the plot_data_path is located.
    """
    # This so user dont hvae to think bout extension and if they do itll also be fine
    if not pdf_name.lower().endswith(".pdf"):
        pdf_name += ".pdf"
    # Load data
    if isinstance(plot_data_path, str):
        plot_data = load(plot_data_path)
    else:
        raise ValueError("plot_data_path should be a string path to a .joblib file")

    # Set output folder to same directory as plot_data_path if not provided
    if output_folder is None:
        output_folder = os.path.dirname(plot_data_path)

    os.makedirs(output_folder, exist_ok=True)
    pdf_path = os.path.join(output_folder, pdf_name)
    with PdfPages(pdf_path) as pdf:
        for sample_id, plot_item in plot_data.items():
            if "Flagged" in plot_item:
                continue  # Skip flagged entries

            file_name = plot_item["profile"]["title"].split(" ")[-1]
            sample_short = file_name.split(".")[0]

            # --- Setup master figure for one sample (4 stacked rows) ---
            fig = plt.figure(figsize=(8.5, 12))
            outer_gs = gridspec.GridSpec(
                4, 1, hspace=0.4, height_ratios=[1, 1, 1.1, 1.1]
            )

            # --- Row 1: Profile, GPA, Dimless Kratky ---
            gs1 = gridspec.GridSpecFromSubplotSpec(
                1, 3, subplot_spec=outer_gs[0], wspace=0.4
            )
            axs = [fig.add_subplot(gs1[0, i]) for i in range(3)]

            axs[0].errorbar(
                plot_item["profile"]["x"],
                plot_item["profile"]["y"],
                plot_item["profile"]["yerr"],
                ecolor="g",
                fmt="bo",
                markersize=2,
                elinewidth=0.5,
            )
            axs[0].set_yscale("log")
            axs[0].set_title(file_name, fontsize=7.5)
            axs[0].set_xlabel(r"$q$ $(\mathrm{\AA}^{-1})$", fontsize=7)
            axs[0].set_ylabel(r"$log(I(q))$", fontsize=7)
            axs[0].tick_params(axis="both", which="major", labelsize=7)

            axs[1].plot(
                plot_item["GPA"]["x"], plot_item["GPA"]["y"], "ob", markersize=2
            )
            axs[1].set_title("GPA", fontsize=7.5)
            axs[1].set_xlabel(r"$q^2$ $(\mathrm{\AA}^{-2})$", fontsize=7)
            axs[1].xaxis.get_offset_text().set_fontsize(6.5)
            axs[1].set_ylabel(f"${plot_item['GPA']['ylabel']}$", fontsize=7)
            axs[1].ticklabel_format(style="sci", axis="x", scilimits=(-2, 2))
            axs[1].ticklabel_format(style="sci", axis="y", scilimits=(-2, 2))
            axs[1].tick_params(axis="both", which="major", labelsize=7)

            axs[2].plot(
                plot_item["Dimless Kratky"]["x"],
                plot_item["Dimless Kratky"]["y"],
                "ob",
                markersize=2,
            )
            axs[2].set_title("Dimensionless Kratky", fontsize=7.5)
            axs[2].set_xlabel(r"$qR_g$", fontsize=7)
            axs[2].set_ylabel(r"$(qR_g)^2 I(q)/I(0)$", fontsize=7)
            axs[2].axvline(x=3**0.5, color="red", linestyle="--", linewidth=1)
            axs[2].axhline(
                y=1.1, color="red", linestyle="--", label="Globular Crosshairs"
            )
            axs[2].legend(fontsize=6.5, loc="best")
            axs[2].set_xlim([0, 6])
            axs[2].set_ylim([0, 2])
            axs[2].tick_params(axis="both", which="major", labelsize=7)

            # --- Row 2: GPA fits (Auto and Method 1) and GMM Clustering ---
            gs2 = gridspec.GridSpecFromSubplotSpec(
                1, 3, subplot_spec=outer_gs[1], width_ratios=[2.8, 2.8, 0.9], wspace=0.4
            )
            selected = plot_item["Rg Selection"]["Selected Method"]
            for idx, label, rg_key in zip(
                [0, 1],
                ["Auto $R_g$", "PDDF-Informed"],
                ["Auto Rg", "Rg Method 1 Final"],
            ):
                ax = fig.add_subplot(gs2[0, idx])

                # Use this to test -1 auto rg #.get("Rg", -1) == -1

                if rg_key not in plot_item or (
                    rg_key == "Auto Rg" and plot_item[rg_key]["Rg"] == -1
                ):
                    # Method failed — Maybe will add a picture later on
                    # img = mpimg.imread("method_failed.png")
                    # ax.imshow(img)
                    # ax.axis("off")
                    ax.text(
                        0.5,
                        0.5,
                        f"{label} Failed",
                        fontsize=9,
                        ha="center",
                        va="center",
                    )
                    ax.set_axis_off()  # optionally turn off the axis
                    continue  # skip to next subplot
                rg = plot_item[rg_key]["Rg"] if idx == 0 else plot_item[rg_key]["Rg"][0]
                i0 = plot_item[rg_key]["i0"] if idx == 0 else plot_item[rg_key]["i0"][0]
                nmin = (
                    plot_item[rg_key]["nmin"]
                    if idx == 0
                    else plot_item[rg_key]["nmin"][0]
                )
                nmax = (
                    plot_item[rg_key]["nmax"]
                    if idx == 0
                    else plot_item[rg_key]["nmax"][0]
                )
                x_maxs, y_maxs, plot_params = get_dim_GPA2(
                    plot_item["profile"]["y"],
                    plot_item["profile"]["x"],
                    rg,
                    i0,
                    nmin,
                    nmax,
                )
                gpa_ = plot_params["data"]
                ax.plot(gpa_["x"], gpa_["y"], "bo", markersize=3, label="Data")
                ax.plot(
                    gpa_["included_x"],
                    gpa_["included_y"],
                    "o",
                    color="orange",
                    markersize=3,
                    label="Included Data",
                )
                ax.plot(
                    gpa_["guinier_x"], gpa_["guinier_y"], "g--", label="Calculated I(q)"
                )
                for x_val, y_data, y_model in zip(
                    gpa_["x"], gpa_["y"], gpa_["guinier_y"]
                ):
                    ax.plot(
                        [x_val, x_val],
                        [y_data, y_model],
                        color="red",
                        linewidth=1,
                        alpha=0.7,
                    )
                ax.axvline(x=1.5, linestyle="--", color="purple")
                ax.axhline(
                    y=np.log(0.7428),
                    linestyle="--",
                    color="purple",
                    label="Ideal Peak Location",
                )
                ax.set_xlabel(r"$(q R_g)^2$", fontsize=7)
                ax.set_ylabel("ln[$q$$R_g$$I(q)$/$I(0)$]", fontsize=7)
                ax.set_xlim([0, 4])
                ax.set_ylim([-2, 0])
                ax.set_title(label, fontsize=7.5)
                ax.legend(fontsize=6.5)
                ax.tick_params(labelsize=7)
                if idx == 1 and selected == "Method 1":
                    for spine in ax.spines.values():
                        spine.set_edgecolor("green")
                        spine.set_linewidth(2)
                elif idx == 0 and selected == "AutoRg":
                    for spine in ax.spines.values():
                        spine.set_edgecolor("green")
                        spine.set_linewidth(2)
                elif idx == 0 and "Auto Rg" in plot_item:
                    # Get makes sure wont crash if no key but if there is will get it
                    nmin = plot_item["Auto Rg"].get("nmin", 0)
                    nmax = plot_item["Auto Rg"].get("nmax", 0)
                    auto_wind = nmax - nmin
                    r2_from_auto = plot_item["Auto Rg"].get("R2", 0)

                    if (auto_wind < 7) or (r2_from_auto < 0.73):
                        # Special case since 0 is an index, so if 0 and window = 6 and r2 is good keep it
                        if not (nmin == 0 and auto_wind == 6 and r2_from_auto >= 0.73):
                            # flag with red spine
                            for spine in ax.spines.values():
                                spine.set_edgecolor("red")
                                spine.set_linewidth(2)

            ax3 = fig.add_subplot(gs2[0, 2])
            prob_found = plot_item["GMM Clustering"]["Probabilities"]
            assigned_cluster = plot_item["GMM Clustering"]["Cluster"]
            probs = [prob_found[f"Cluster {i}"] for i in range(5)]
            labels = ["0 (Fd)", "1 (Pd)", "2 (Ds)", "3 (Gb)", "4 (Fx)"]
            colors = ["red", "skyblue", "green", "orange", "purple"]
            ax3.barh(range(len(probs)), probs, color=colors)
            ax3.set_xlim(0, 1)
            ax3.set_yticks([])
            ax3.set_xticks([0, 0.5, 1.0])
            ax3.set_title("Cluster\nProbabilities", fontsize=7.5)
            ax3.tick_params(axis="x", labelsize=7)
            for i, (label, prob) in enumerate(zip(labels, probs)):
                fontweight = "bold" if i == assigned_cluster else "normal"
                ax3.text(
                    -0.02,
                    i,
                    label,
                    va="center",
                    ha="right",
                    fontsize=6,
                    fontweight=fontweight,
                    transform=ax3.get_yaxis_transform(),
                )
                ax3.text(
                    prob + 0.02,
                    i,
                    f"{prob * 100:.1f}%",
                    va="center",
                    ha="left",
                    fontsize=7,
                )
            for spine in ["top", "right"]:
                ax3.spines[spine].set_visible(False)

            # --- Row 3: Auto & PDDF-Informed Guinier Residuals ---
            gs3 = gridspec.GridSpecFromSubplotSpec(
                2,
                2,
                subplot_spec=outer_gs[2],
                height_ratios=[2.5, 1],
                wspace=0.25,
                hspace=0.1,
            )

            # ---------- Left Column: Auto Guinier ----------
            if "Auto Rg" not in plot_item or plot_item["Auto Rg"].get("Rg", -1) == -1:
                ax_top = fig.add_subplot(gs3[0, 0])
                ax_bot = fig.add_subplot(gs3[1, 0], sharex=ax_top)
                ax_top.set_title("Auto Guinier Failed", fontsize=7)
                ax_bot.set_title("Auto Guinier Failed", fontsize=7)
                ax_top.axis("off")
                ax_bot.axis("off")
            else:  # For if auto fails plotting will be fine for the method that worked
                results_auto = get_residuals_guinier_plot(
                    plot_item["profile"]["y"],
                    plot_item["profile"]["x"],
                    plot_item["profile"]["yerr"],
                    plot_item["Auto Rg"]["nmin"],
                    plot_item["Auto Rg"]["nmax"],
                )
                ax_top = fig.add_subplot(gs3[0, 0])
                ax_bot = fig.add_subplot(gs3[1, 0], sharex=ax_top)

                ax_top.plot(
                    results_auto["x_all"],
                    results_auto["y_all"],
                    "o",
                    color="gray",
                    alpha=0.8,
                    markersize=2,
                )
                ax_top.plot(
                    results_auto["x_fit"],
                    results_auto["y_fit"],
                    "o",
                    color="blue",
                    markersize=2,
                )
                ax_top.plot(
                    results_auto["x_fit"],
                    results_auto["y_model"],
                    "-",
                    color="red",
                    linewidth=1,
                    label=r"$R^2$ " + str(round(plot_item["Auto Rg"]["R2"], 3)),
                )
                ax_top.set_title(
                    "Auto Guinier: $R_g$: "
                    + str(round(plot_item["Auto Rg"]["Rg"], 2))
                    + r"$\pm$"
                    + str(round(plot_item["Auto Rg"]["Rg Err"], 2)),
                    fontsize=7,
                )

                ax_top.set_ylabel(r"$\ln[I(q)]$", fontsize=7)
                ax_top.tick_params(axis="both", which="major", labelsize=7)
                ax_top.axvline(
                    x=results_auto["x_fit"][0], linestyle="--", color="red", linewidth=1
                )
                ax_top.axvline(
                    x=results_auto["x_fit"][-1],
                    linestyle="--",
                    color="red",
                    linewidth=1,
                )
                ax_top.set_ylim(
                    [
                        results_auto["y_model"].min() - 0.5,
                        results_auto["y_all"].max() + 0.5,
                    ]
                )
                ax_top.set_xlim(
                    # [0, results_auto["x_fit"][-1] + (results_auto["x_fit"].ptp() * 0.10)]
                    [
                        0,
                        results_auto["x_fit"][-1]
                        + (np.ptp(results_auto["x_fit"]) * 0.10),
                    ]
                )
                ax_top.tick_params(labelbottom=False)  # hides x-tick labels on top
                ax_top.legend(fontsize=6.5, loc="upper right")

                # After ax_top.set_title(...)
                warning_lines = []

                # Check thresholds
                if plot_item["Auto Rg"].get("R2", 1) < 0.73:
                    warning_lines.append(r"$R^2$ < 0.73")
                if (nmax - nmin) < 7:
                    # Special case: nmin=0 and nmax=6 → actually 7 points
                    # if not (nmin == 0 and (nmax - nmin) == 6): #ccommented bc this wouldnt flag less than it, so gotta be stright up 6
                    if not (nmin == 0 and nmax == 6):
                        warning_lines.append("Fewer than 7 points")

                # If any warnings exist, plot the text
                if warning_lines:
                    warning_text = "\n".join(warning_lines)
                    ax_top.text(
                        0.95,
                        0.05,  # Position: bottom-right corner in axes coords
                        warning_text,
                        transform=ax_top.transAxes,
                        fontsize=6.5,
                        color="red",
                        ha="right",
                        va="bottom",
                        bbox=dict(
                            boxstyle="round,pad=0.3",
                            edgecolor="red",
                            facecolor="white",
                            alpha=0.8,
                        ),
                    )

                ax_bot.plot(
                    results_auto["x_fit"], results_auto["residuals"], "b-", linewidth=1
                )
                ax_bot.axhline(y=0, linestyle="--", color="red", linewidth=1)
                ax_bot.set_xlabel(r"$q^2$ $(\mathrm{\AA}^{-2})$", fontsize=7)
                ax_bot.xaxis.set_major_formatter(FormatStrFormatter("%.4f"))
                ax_bot.set_ylabel(r"$\Delta \ln[I(q)] / \sigma(q)$", fontsize=7)
                ax_bot.tick_params(axis="both", which="major", labelsize=7)

            # ---------- Right Column: Method 1 ----------
            if "Rg Method 1 Final" not in plot_item:  # If method 1 failed
                ax_top = fig.add_subplot(gs3[0, 1])
                ax_bot = fig.add_subplot(gs3[1, 1], sharex=ax_top)
                ax_top.set_title("Method 1 Failed", fontsize=7)
                ax_bot.set_title("Method 1 Failed", fontsize=7)
                ax_top.axis("off")
                ax_bot.axis("off")
            else:
                results_m1 = get_residuals_guinier_plot(
                    plot_item["profile"]["y"],
                    plot_item["profile"]["x"],
                    plot_item["profile"]["yerr"],
                    plot_item["Rg Method 1 Final"]["nmin"][0],
                    plot_item["Rg Method 1 Final"]["nmax"][0],
                )
                ax_top = fig.add_subplot(gs3[0, 1])
                ax_bot = fig.add_subplot(gs3[1, 1], sharex=ax_top)

                # ax_top, ax_bot = axes[0, 1], axes[1, 1]

                ax_top.plot(
                    results_m1["x_all"],
                    results_m1["y_all"],
                    "o",
                    color="gray",
                    alpha=0.8,
                    markersize=2,
                )
                ax_top.plot(
                    results_m1["x_fit"],
                    results_m1["y_fit"],
                    "o",
                    color="blue",
                    markersize=2,
                )
                ax_top.plot(
                    results_m1["x_fit"],
                    results_m1["y_model"],
                    "-",
                    color="red",
                    linewidth=1,
                    label=r"$R^2$ "
                    + str(round(plot_item["Rg Method 1 Final"]["fit_r2"][0], 3)),
                )
                ax_top.set_title(
                    "PDDF-Informed: $R_g$: "
                    + str(round(plot_item["Rg Method 1 Final"]["Rg"][0], 2))
                    + r"$\pm$"
                    + str(round(plot_item["Rg Method 1 Final"]["Rg Err"][0], 2)),
                    fontsize=7,
                )

                ax_top.set_ylabel(r"$\ln[I(q)]$", fontsize=7)
                ax_top.tick_params(axis="both", which="major", labelsize=7)
                ax_top.axvline(
                    x=results_m1["x_fit"][0], linestyle="--", color="red", linewidth=1
                )
                ax_top.axvline(
                    x=results_m1["x_fit"][-1], linestyle="--", color="red", linewidth=1
                )
                ax_top.set_ylim(
                    [results_m1["y_model"].min() - 0.5, results_m1["y_all"].max() + 0.5]
                )
                ax_top.set_xlim(
                    [0, results_m1["x_fit"][-1] + (np.ptp(results_m1["x_fit"] * 0.10))]
                    # [0, results_m1["x_fit"][-1] + (results_m1["x_fit"].ptp() * 0.10)] #Not compatibl w numpy2.0.0
                )
                ax_top.tick_params(labelbottom=False)  # hides x-tick labels on top
                ax_top.legend(fontsize=6.5, loc="upper right")

                ax_bot.plot(
                    results_m1["x_fit"], results_m1["residuals"], "b-", linewidth=1
                )
                ax_bot.axhline(y=0, linestyle="--", color="red", linewidth=1)
                ax_bot.set_xlabel(r"$q^2$ $(\mathrm{\AA}^{-2})$", fontsize=7)
                ax_bot.xaxis.set_major_formatter(FormatStrFormatter("%.4f"))
                ax_bot.set_ylabel(r"$\Delta \ln[I(q)] / \sigma(q)$", fontsize=7)
                ax_bot.tick_params(axis="both", which="major", labelsize=7)

            # Row 4 PDDF

            # ======= Left panel: PDDF Fit + Residuals =======
            gs4 = gridspec.GridSpecFromSubplotSpec(
                1, 2, subplot_spec=outer_gs[3], width_ratios=[3.2, 2.8], wspace=0.3
            )
            gs4_left = gridspec.GridSpecFromSubplotSpec(
                2, 1, subplot_spec=gs4[0], height_ratios=[2, 1], hspace=0.05
            )

            # Top: Fit
            # ax_fit = fig.add_subplot(gs4_left[0])
            # [your plotting code for fit...]

            # ======= Right panel: PDDF Plot =======
            # ax_pddf = fig.add_subplot(gs4[1])
            # [your PDDF curve plotting code...]

            # Top: Fit
            ax_fit = fig.add_subplot(gs4_left[0])
            ax_fit.plot(
                plot_item["pr_plot"]["pr_q_orig"],
                plot_item["pr_plot"]["pr_i_orig"],
                "o",
                color="blue",
                alpha=0.8,
                markersize=2,
                label="Data",
                linewidth=1,
            )
            ax_fit.plot(
                plot_item["pr_residuals"]["q_extrapolated"][1:],
                plot_item["pr_residuals"]["i_fit"],
                color="red",
                linewidth=1,
                label="Fitted Region",
            )
            ax_fit.set_yscale("log")
            ax_fit.set_title("Data/Fit", fontsize=7.5)

            ax_fit.set_ylabel(r"$I(q)$", fontsize=7)
            ax_fit.tick_params(axis="both", which="major", labelsize=7)
            ax_fit.legend(fontsize=7)

            # Bottom: Residuals
            ax_res = fig.add_subplot(gs4_left[1], sharex=ax_fit)
            ax_res.plot(
                plot_item["pr_residuals"]["residuals_x"],
                plot_item["pr_residuals"]["residuals_y"],
                "b-",
                linewidth=1,
            )
            ax_res.axhline(y=0, linestyle="--", color="red", linewidth=1)

            ax_res.set_xlabel(r"$q$ $(\mathrm{\AA})$", fontsize=7)
            ax_res.set_ylabel(r"$\Delta [I(q)]/\sigma(q)$", fontsize=7)
            ax_res.tick_params(axis="both", which="major", labelsize=7)

            # ======= Right panel: PDDF Plot =======
            predicted_dmax = plot_item["Predicted Dmax"]["prediction"]
            BIFT_dmax = plot_item["pr_plot"]["x"][-1]
            diff_dmax = (abs(predicted_dmax - BIFT_dmax) / BIFT_dmax) * 100

            ax_pddf = fig.add_subplot(gs4[1])
            ax_pddf.plot(
                plot_item["pr_plot"]["x"],
                plot_item["pr_plot"]["y"],
                "bo-",
                markersize=2,
                linewidth=1.5,
                label=f"BIFT $D_{{max}}$ = {BIFT_dmax:.1f} Å",
            )

            ax_pddf.set_xlabel(r"$r$ $(\mathrm{\AA})$", fontsize=7)
            ax_pddf.set_ylabel(r"$P(r)$", fontsize=7)
            xmax = max(predicted_dmax, BIFT_dmax)
            ax_pddf.set_xlim(0, xmax * 1.05)
            ax_pddf.set_ylim(bottom=0)
            ax_pddf.tick_params(axis="both", which="major", labelsize=7.5)
            ax_pddf.set_title(
                "PDDF $R_g$:"
                + str(round(plot_item["pr_plot"]["Rg"], 2))
                + "+/-"
                + str(round(plot_item["pr_plot"]["Rg err"], 2)),
                fontsize=7.5,
            )

            # Optional: vertical Dmax line
            if diff_dmax < 20:
                ax_pddf.axvline(
                    predicted_dmax,
                    color="green",
                    linestyle="--",
                    linewidth=1.5,
                    alpha=0.7,
                    label=f"Predicted $D_{{max}}$ = {predicted_dmax:.1f} Å",
                )
            elif diff_dmax >= 20:
                ax_pddf.axvline(
                    predicted_dmax,
                    color="red",
                    linestyle="--",
                    linewidth=1.5,
                    alpha=0.7,
                    label=f"Predicted $D_{{max}}$ = {predicted_dmax:.1f} Å",
                )

            ax_pddf.legend(fontsize=7)

            # fig.savefig(f'SI1_row4_Pr_residuals_{id}.png', dpi=300, bbox_inches='tight')
            # plt.show()

            pdf.savefig(fig)
            plt.close(fig)

    print(f"Saved PDF summary to {pdf_path}")
    return pdf_path


def get_dim_GPA2(I, q, rg, i0, nmin, nmax, plot=False):
    """Another Dimensionless GPA function that uses the same logic as get_dim_GPA but with different outputs, in
    the format of dictionary for plotting.
    Args:
        I (array): Intensity data.
        q (array): q values.
        rg (float): Radius of gyration.
        i0 (float): Intensity at zero angle.
        nmin (int): Minimum index for the range of interest.
        nmax (int): Maximum index for the range of interest.
        Returns:
        x_maxs (float): Maximum x value.
        y_maxs (float): Maximum y value.
        plot_params (dict): Dictionary containing plot parameters.
    """
    # This happens w krarkys sometimes, just plotting so turned it off
    with np.errstate(divide="ignore", invalid="ignore"):
        y = np.log((q * rg * I) / i0)
    x = (q * rg) ** 2
    index_max_y = np.argmax(y)
    index_max_plot = np.argmin(abs(x - 4))
    x_mins, x_maxs, y_mins, y_maxs = min_max_function(
        y[:index_max_plot], x[:index_max_plot]
    )

    # Prepare plot data for saving
    plot_params = {
        "type": "Dimensionless GPA",
        "data": {
            "x": x,
            "y": y,
            "included_x": x[nmin : nmax + 1],
            "included_y": y[nmin : nmax + 1],
            "guinier_x": x,
            "guinier_y": np.log((q * rg * (i0 * np.exp(-((rg**2 * q**2) / 3)))) / i0),
        },
        "lines": [
            {
                "x": [1.5, 1.5],
                "y": [-2, 0],
                "style": "--",
                "label": "Ideal Vertical Line",
            },
            {
                "x": [0, 4],
                "y": [np.log(0.7428), np.log(0.7428)],
                "style": "--",
                "label": "Ideal Horizontal Line",
            },
        ],
        "labels": {
            "title": "Dim GPA Rg: Peak",
            "xlabel": "$(Rgq)^2$",
            "ylabel": "ln[qRgI(q)/I(0)]",
        },
        "limits": {"xlim": [0, 4], "ylim": [-2, 0]},
    }

    if plot == True:
        fig, ax = plt.subplots()
        # Plot data
        ax.plot(plot_params["data"]["x"], plot_params["data"]["y"], "o", label="Data")
        ax.plot(
            plot_params["data"]["included_x"],
            plot_params["data"]["included_y"],
            "o",
            label="Included",
        )
        ax.plot(
            plot_params["data"]["guinier_x"],
            plot_params["data"]["guinier_y"],
            "--",
            label="Guinier Approximation",
        )
        # Plot lines
        for line in plot_params["lines"]:
            ax.plot(line["x"], line["y"], line["style"], label=line["label"])
        # Set labels and limits
        ax.set_title(plot_params["labels"]["title"])
        ax.set_xlabel(plot_params["labels"]["xlabel"])
        ax.set_ylabel(plot_params["labels"]["ylabel"])
        ax.set_xlim(plot_params["limits"]["xlim"])
        ax.set_ylim(plot_params["limits"]["ylim"])
        ax.legend()
        plt.show()

    return x_maxs, y_maxs, plot_params


def export_solved_plots(joblib_path):
    """
    Extracts selected plot data from unflagged entries in plot_data and writes them to Excel.
    A folder is created per sample inside a 'plots' directory next to the joblib file.
    """

    plot_data = load(joblib_path)
    root_dir = os.path.dirname(joblib_path)
    plots_dir = os.path.join(root_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    selected_keys = [
        "profile",
        "GPA",
        "kratky",
        "pr_plot",
        "pr_residuals",
        "Dimless Kratky",
    ]

    for sample_id, plots in plot_data.items():
        if "Flagged" in plots:
            continue

        sample_folder = os.path.join(plots_dir, sample_id)
        os.makedirs(sample_folder, exist_ok=True)
        plot_item = plot_data[
            sample_id
        ]  # redefined this bc just copied the guiner extraction from runner so easier fro me

        for key in selected_keys:
            if key not in plots:
                continue

            data = plots[key]

            if key == "pr_residuals":
                x_vals = data.get("residuals_x", [])
                y_vals = data.get("residuals_y", [])
                xlabel = "x"
                ylabel = "y"

                df = pd.DataFrame({xlabel: x_vals, ylabel: y_vals})
                filename = "pr_residuals.xlsx"
                filepath = os.path.join(sample_folder, filename)
                df.to_excel(filepath, index=False)

                x_vals = data.get("q_extrapolated", [])
                y_vals = data.get("i_fit", [])
                x_vals = x_vals[1:]

                xlabel = "x"
                ylabel = "y"

                df = pd.DataFrame({xlabel: x_vals, ylabel: y_vals})
                filename = "Pr_fit_q_n_i.xlsx"
                filepath = os.path.join(sample_folder, filename)
                df.to_excel(filepath, index=False)

            if key == "pr_plot":
                x_vals = data.get("pr_q_orig", [])
                y_vals = data.get("pr_i_orig", [])

                xlabel = "x"
                ylabel = "y"

                df = pd.DataFrame({xlabel: x_vals, ylabel: y_vals})
                filename = "Pr_fit_orig_q_n_i_.xlsx"
                filepath = os.path.join(sample_folder, filename)
                df.to_excel(filepath, index=False)

                x_vals = data.get("x", [])
                y_vals = data.get("y", [])

                xlabel = "x"
                ylabel = "y"

                df = pd.DataFrame({xlabel: x_vals, ylabel: y_vals})
                filename = "pr.xlsx"
                filepath = os.path.join(sample_folder, filename)
                df.to_excel(filepath, index=False)

            if key == "profile":
                x_vals = data.get("x", [])
                y_vals = data.get("y", [])
                y_vals1 = data.get("yerr", [])  # error

                xlabel = "x"
                ylabel = "y"
                ylabel1 = "yerr"

                df = pd.DataFrame({xlabel: x_vals, ylabel: y_vals, ylabel1: y_vals1})
                filename = f"{key.replace(' ', '_')}.xlsx"
                filepath = os.path.join(sample_folder, filename)
                df.to_excel(filepath, index=False)

            if key in ["GPA", "kratky", "Dimless Kratky"]:
                x_vals = data.get("x", [])
                y_vals = data.get("y", [])

                xlabel = "x"
                ylabel = "y"

                df = pd.DataFrame({xlabel: x_vals, ylabel: y_vals})
                filename = f"{key.replace(' ', '_')}.xlsx"
                filepath = os.path.join(sample_folder, filename)
                df.to_excel(filepath, index=False)

            if "Auto Rg" in plot_item or plot_item["Auto Rg"].get("Rg", -1) > 0:
                results_auto = get_residuals_guinier_plot(
                    plot_item["profile"]["y"],
                    plot_item["profile"]["x"],
                    plot_item["profile"]["yerr"],
                    plot_item["Auto Rg"]["nmin"],
                    plot_item["Auto Rg"]["nmax"],
                )
                x_all = results_auto["x_all"]
                y_all = results_auto["y_all"]
                x_fit = results_auto["x_fit"]
                y_fit = results_auto["y_fit"]
                y_model = results_auto["y_model"]
                residual = results_auto["residuals"]

                # lookup dictionaries
                fit_dict = dict(zip(x_fit, y_fit))
                model_dict = dict(zip(x_fit, y_model))
                x_fit_dict = {x: x for x in x_fit}
                residual_dict = dict(zip(x_fit, residual))

                # aligned lists

                aligned_y_fit = [fit_dict.get(x, np.nan) for x in x_all]
                aligned_y_model = [model_dict.get(x, np.nan) for x in x_all]
                aligned_x_fit = [x_fit_dict.get(x, np.nan) for x in x_all]
                aligned_residuals = [residual_dict.get(x, np.nan) for x in x_all]

                # Final DataFrame
                df = pd.DataFrame(
                    {
                        "x_all": x_all,
                        "y_all": y_all,
                        "y_fitted_data": aligned_y_fit,
                        "y_model": aligned_y_model,
                        "residuals": aligned_residuals,
                        "x_fit": aligned_x_fit,
                    }
                )

                filename = "auto_guinier_.xlsx"
                filepath = os.path.join(sample_folder, filename)
                df.to_excel(filepath, index=False)

                x_maxs, y_maxs, plot_params = get_dim_GPA2(
                    plot_item["profile"]["y"],
                    plot_item["profile"]["x"],
                    plot_item["Auto Rg"]["Rg"],
                    plot_item["Auto Rg"]["i0"],
                    plot_item["Auto Rg"]["nmin"],
                    plot_item["Auto Rg"]["nmax"],
                )
                gpa_ = plot_params["data"]

                # Extract all aligned values
                x_all = gpa_.get("x", [])
                y_all = gpa_.get("y", [])
                included_x = gpa_.get("included_x", [])
                included_y = gpa_.get("included_y", [])
                model_y = gpa_.get(
                    "guinier_y",
                    [],
                )

                # Build dictionaries to align fits to x_all
                included_dict = dict(zip(included_x, included_y))
                model_dict = dict(
                    zip(x_all, model_y)
                )  # Assumes model_y is aligned with x

                # Align values
                aligned_included_y = [included_dict.get(x, np.nan) for x in x_all]
                aligned_model_y = [model_dict.get(x, np.nan) for x in x_all]
                aligned_included_x = [x if x in included_x else np.nan for x in x_all]

                df = pd.DataFrame(
                    {
                        "x_all": x_all,
                        "y_all": y_all,
                        "y_included": aligned_included_y,
                        "y_model": aligned_model_y,
                        "included_x": aligned_included_x,
                        "guinier_x": gpa_.get("guinier_x", []),
                        "guinier_y": gpa_.get("guinier_y", []),
                    }
                )

                filename = "Dimless_GPA_fit_auto_guinier.xlsx"
                filepath = os.path.join(sample_folder, filename)
                df.to_excel(filepath, index=False)

            if "Rg Method 1 Final" in plot_item:
                results_m1 = get_residuals_guinier_plot(
                    plot_item["profile"]["y"],
                    plot_item["profile"]["x"],
                    plot_item["profile"]["yerr"],
                    plot_item["Rg Method 1 Final"]["nmin"][0],
                    plot_item["Rg Method 1 Final"]["nmax"][0],
                )
                x_all = results_m1["x_all"]
                y_all = results_m1["y_all"]
                x_fit = results_m1["x_fit"]
                y_fit = results_m1["y_fit"]
                y_model = results_m1["y_model"]
                residual = results_m1["residuals"]
                # lookup dictionaries
                fit_dict = dict(zip(x_fit, y_fit))
                residual_dict = dict(zip(x_fit, residual))
                model_dict = dict(zip(x_fit, y_model))
                x_fit_dict = {x: x for x in x_fit}

                # aligned lists
                aligned_y_fit = [fit_dict.get(x, np.nan) for x in x_all]
                aligned_y_model = [model_dict.get(x, np.nan) for x in x_all]
                aligned_residuals = [residual_dict.get(x, np.nan) for x in x_all]
                aligned_x_fit = [x_fit_dict.get(x, np.nan) for x in x_all]
                # Final DataFrame
                df = pd.DataFrame(
                    {
                        "x_all": x_all,
                        "y_all": y_all,
                        "y_fitted_data": aligned_y_fit,
                        "y_model": aligned_y_model,
                        "residuals": aligned_residuals,
                        "x_fit": aligned_x_fit,
                    }
                )

                filename = "Method1_Guinier_.xlsx"
                filepath = os.path.join(sample_folder, filename)
                df.to_excel(filepath, index=False)

                x_maxs, y_maxs, plot_params = get_dim_GPA2(
                    plot_item["profile"]["y"],
                    plot_item["profile"]["x"],
                    plot_item["Rg Method 1 Final"]["Rg"][0],
                    plot_item["Rg Method 1 Final"]["i0"][0],
                    plot_item["Rg Method 1 Final"]["nmin"][0],
                    plot_item["Rg Method 1 Final"]["nmax"][0],
                )
                gpa_ = plot_params["data"]

                # Extract all aligned values
                x_all = gpa_.get("x", [])
                y_all = gpa_.get("y", [])
                included_x = gpa_.get("included_x", [])
                included_y = gpa_.get("included_y", [])
                model_y = gpa_.get("guinier_y", [])

                # Build dictionaries to align fits to x_all
                included_dict = dict(zip(included_x, included_y))
                model_dict = dict(
                    zip(x_all, model_y)
                )  # Assumes model_y is aligned with x

                # Align values
                aligned_included_y = [included_dict.get(x, np.nan) for x in x_all]
                aligned_included_x = [x if x in included_x else np.nan for x in x_all]
                aligned_model_y = [model_dict.get(x, np.nan) for x in x_all]

                df = pd.DataFrame(
                    {
                        "x_all": x_all,
                        "y_all": y_all,
                        "y_included": aligned_included_y,
                        "y_model": aligned_model_y,
                        "included_x": aligned_included_x,
                        "guinier_x": gpa_.get("guinier_x", []),
                        "guinier_y": gpa_.get("guinier_y", []),
                    }
                )

                filename = "Dimless_GPA_fit_Method1.xlsx"
                filepath = os.path.join(sample_folder, filename)
                df.to_excel(filepath, index=False)
