# Re-importing necessary packages after code execution state reset
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from joblib import load
from saxs_assistant.utils.helpers import clean_path


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


def plot_flagged(plot_data_path, output_folder=None, pdf_name="flagged_summary.pdf"):
    """
    Plots the flagged data files (those with 'Flagged' key).
    Creates a PDF with ~4 samples per page (1 row per sample, each row has 3 plots).
    """

    plot_data_path = clean_path(plot_data_path)

    if not pdf_name.lower().endswith(".pdf"):
        pdf_name += ".pdf"

    if isinstance(plot_data_path, str):
        plot_data = load(plot_data_path)
    else:
        raise ValueError("plot_data_path should be a string path to a .joblib file")

    if output_folder is None:
        output_folder = os.path.dirname(plot_data_path)

    os.makedirs(output_folder, exist_ok=True)
    pdf_path = os.path.join(output_folder, pdf_name)

    flagged_items = [
        (sample_id, item) for sample_id, item in plot_data.items() if "Flagged" in item
    ]

    with PdfPages(pdf_path) as pdf:
        for i in range(0, len(flagged_items), 4):  # 4 samples per page
            fig, axs = plt.subplots(4, 3, figsize=(8.5, 10))  # 4 rows, 3 columns

            for j in range(4):  # Always iterate 4 times
                if i + j >= len(flagged_items):
                    # Hide unused axes
                    for ax in axs[j]:
                        ax.set_visible(False)
                    continue

                sample_id, plot_item = flagged_items[i + j]
                row = axs[j]

                # --- Profile Plot ---
                ax = row[0]
                file_name = plot_item["profile"]["title"].split(" ")[-1]
                ax.errorbar(
                    plot_item["profile"]["x"],
                    plot_item["profile"]["y"],
                    plot_item["profile"]["yerr"],
                    ecolor="g",
                    fmt="bo",
                    markersize=2,
                    elinewidth=0.5,
                )
                ax.set_yscale("log")
                ax.set_title(file_name, fontsize=7.5)
                ax.set_xlabel(r"$q$ $(\mathrm{\AA}^{-1})$", fontsize=7)
                ax.set_ylabel(r"$log(I(q))$", fontsize=7)
                ax.tick_params(axis="both", which="major", labelsize=7)

                # --- GPA Plot ---
                ax = row[1]
                ax.plot(
                    plot_item["GPA"]["x"], plot_item["GPA"]["y"], "ob", markersize=2
                )
                ax.set_title("GPA", fontsize=7.5)
                ax.set_xlabel(r"$q^2$ $(\mathrm{\AA}^{-2})$", fontsize=7)
                ax.ticklabel_format(style="sci", axis="x", scilimits=(-2, 2))
                ax.xaxis.get_offset_text().set_fontsize(6.5)
                ax.set_ylabel(f"${plot_item['GPA']['ylabel']}$", fontsize=7)
                ax.tick_params(axis="both", which="major", labelsize=7)

                # --- Kratky Plot ---
                ax = row[2]
                ax.plot(
                    plot_item["kratky"]["x"],
                    plot_item["kratky"]["y"],
                    "ob",
                    markersize=2,
                )
                ax.set_title("Kratky", fontsize=7.5)
                ax.set_xlabel(r"$q$ $(\mathrm{\AA}^{-1})$", fontsize=7)
                ax.set_ylabel(r"$q^2I(q)$", fontsize=7)
                ax.ticklabel_format(style="sci", axis="y", scilimits=(-2, 2))
                ax.tick_params(axis="both", which="major", labelsize=7)

            # for j, (sample_id, plot_item) in enumerate(flagged_items[i : i + 4]):
            #     row = axs[j]
            #     print(sample_id)

            #     # --- Profile Plot ---
            #     ax = row[0]
            #     file_name = plot_item["profile"]["title"].split(" ")[-1]
            #     ax.errorbar(
            #         plot_item["profile"]["x"],
            #         plot_item["profile"]["y"],
            #         plot_item["profile"]["yerr"],
            #         ecolor="g",
            #         fmt="bo",
            #         markersize=2,
            #         elinewidth=0.5,
            #     )
            #     ax.set_yscale("log")
            #     ax.set_title(file_name, fontsize=7.5)
            #     ax.set_xlabel(r"$q$ $(\mathrm{\AA}^{-1})$", fontsize=7)
            #     ax.set_ylabel(r"$log(I(q))$", fontsize=7)
            #     ax.tick_params(axis="both", which="major", labelsize=7)

            #     # --- GPA Plot ---
            #     ax = row[1]
            #     ax.plot(
            #         plot_item["GPA"]["x"], plot_item["GPA"]["y"], "ob", markersize=2
            #     )
            #     ax.set_title("GPA", fontsize=7.5)
            #     ax.set_xlabel(r"$q$ $(\mathrm{\AA}^{-2})$", fontsize=7)
            #     ax.ticklabel_format(style="sci", axis="x", scilimits=(-2, 2))
            #     ax.xaxis.get_offset_text().set_fontsize(6.5)
            #     ax.set_ylabel(f"${plot_item['GPA']['ylabel']}$", fontsize=7)
            #     ax.tick_params(axis="both", which="major", labelsize=7)

            #     # --- Kratky Plot ---
            #     ax = row[2]
            #     ax.plot(
            #         plot_item["kratky"]["x"],
            #         plot_item["kratky"]["y"],
            #         "ob",
            #         markersize=2,
            #     )
            #     ax.set_title("Kratky", fontsize=7.5)
            #     ax.set_xlabel(r"$q$ $(\mathrm{\AA}^{-1})$", fontsize=7)
            #     ax.set_ylabel(r"$q^2I(q)$", fontsize=7)
            #     ax.tick_params(axis="both", which="major", labelsize=7)

            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    print(f"Saved flagged PDF summary to {pdf_path}")
    return pdf_path
