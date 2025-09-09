
#  SAXS Assistant

**SAXS Assistant** is a plug-and-play Python package for automating SAXS (Small-Angle X-ray Scattering) data analysis. It streamlines the entire process — from file preparation to result visualization — with a single command.

---

##  Installation

### Standard
```bash
pip install saxs-assistant

***For Google Colab use
!pip install saxs-assistant 
```

### With optional music playback  (for local environments only- not for colab)
```bash
pip install saxs-assistant[music]
```

---

##  Quick Start

### 1. Analyze Your Data

```python
from saxs_assistant.runner import analyze_and_plot_all

plot_data, results = analyze_and_plot_all("path/to/input_file.xlsx")
```

This will:
- Run analysis on all entries in the input file
- Save plots and results in a `return/` folder
- Print status updates and return:
  - `plot_data`: dictionary for visualizations
  - `results`: pandas dataframe of SAXS outputs
  - solved_only: pandas dataframe of SAXS outputs without any files that have "Fatal Flag" entry or missing Pr/Guinier Rg
  -unsolved_only: Dataframe having only the files that werent solved
  -plots folder: This has the raw graph data for the solved files will be saved in the same directory to where the PDF summary plots are solved

#### Optional arguments
```python
analyze_and_plot_all(
    df_path="input_file.xlsx",
    start_index=50,     # Start analysis at row 50 of the input file
    end_index=100,      # End at row 100 (non-inclusive)
    output_dir="my_results",  # Override output folder
    music=True          # Play background music (if installed locally)
)
```

---

### 2. Generate an Input File

Use this if you don’t already have a dataframe:
```python
from saxs_assistant.runner import prepare_dataframe

df = prepare_dataframe(folder_path="path/to/folder", angular_unit="1/A")
```

This scans your folder and creates an Excel input file containing:
- File names and paths
- Angular unit (must be `'1/A'` or `'1/nm'`)

Saved as: `input_df_<date>.xlsx` in the parent folder.
***Note all files must be .dat SAXS profiles otherwise code will error if another file type (e.g., excel) is present in this folder.

---

### 3. Combine Multiple Sessions (Optional)

If you run `analyze_and_plot_all()` multiple times, each run will create folders like:
- `return/`
- `return_1/`
- `return_2/`  
...in the same parent directory.

To merge the results:
```python
from saxs_assistant.organizer import combine_sessions

combine_sessions(base_path="path/to/folder")
```

This will:
- Combine all `results.xlsx` and `plot_data.joblib` into a single file
- Save them as:
  - `final_results.xlsx`
  - `final_results_Plots.joblib`
- Move original `return*` folders into a subdirectory called `partials/`

---

##  Expected Input Format

Your Excel input file must contain:
- `file name`: Name of each SAXS file
- `path`: Folder containing the file
- `Angular unit`: Either `1/A` or `1/nm`

You can generate this automatically using `prepare_dataframe()` or create it manually.

---

##  Output

All outputs are stored in a `/return/` folder unless otherwise specified:
- `results.xlsx`: All extracted parameters
- `plot_data.joblib`: Data dictionary for visualization
- `summary_plots.pdf`: Auto-generated plots of good fits
- `flagged_plots.pdf`: Highlighted issues or low-quality data

---

##  Optional: Music Playback

Add a little ambiance during analysis:
```python
analyze_and_plot_all("input.xlsx", music=True)
```

Note:
- Only works on local machines
- Automatically skipped in cloud environments (e.g., Colab)

---

##  Example Use Case

```python
# Step 1: Prepare input
prepare_dataframe(folder_path="saxs_data", angular_unit="1/A")

# Step 2: Run analysis
analyze_and_plot_all("input_df_Jun_25_25.xlsx", music=True)

# (optional) Step 3: Combine results from multiple sessions
combine_sessions(base_path="saxs_data")
```

---

##  Dependencies

Automatically installed via `setup.py`.  
To install manually:
```bash
pip install -r requirements.txt
```

For music playback:
```bash
pip install playsound
```

---

##  License

GPLv3

---

##  Acknowledgments

Developed for efficient SAXS exploration — may it help others find structure in the scatter.
SAXS Assisant does not offer warranty-- use at your own risk and evaluate the results carefully.
If you use SAXS Assistant Please Cite RAW and BIFT, and Franke et. al

Hansen, S. Journal of Applied Crystallography (2000) 33, 1415-1421. DOI: 10.1107/S0021889800012930

https://doi.org/10.1107/S1600576723011019
https://doi.org/10.1107/S0021889809023863
https://doi.org/10.1016/j.bpj.2018.04.018
