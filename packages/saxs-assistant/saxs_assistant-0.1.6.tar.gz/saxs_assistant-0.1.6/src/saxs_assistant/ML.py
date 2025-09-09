"""This contains functions relating to the use of Machine Learning in SAXS data analysis.
Including the clustering and the prediction of Dmax using a MLP regressor
trained on SASBDB data
"""


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
import logging
from joblib import load
from scipy.integrate import quad, trapezoid
from saxs_assistant import models
from importlib import resources


def load_model(filename: str):
    with resources.path(models, filename) as path:
        bundle = load(path)
    return bundle


def compute_franke_features(q, I, rg, i0, sample_id, df, j):
    """
    Computes Franke shape features and stores them only in the dataframe.
    Does NOT touch plot_data.
    """
    try:
        V = get_franke_features2(q, rg, I, i0)
        feature_labels = ["V_1.7", "V_3", "V_4", "V_5", "V_6", "V_7", "V_8"]
        for k, v in zip(feature_labels, V):
            df.loc[df.index[j], k] = v

    except Exception as e:
        logging.warning(f"Franke feature calculation failed for {sample_id}: {e}")

    return df


def predict_dmax_from_features_only(df, j, bundle_path=None):
    # "dmax_predictor_2bundle_05262025.joblib"  -- Now loading in runner to prevent slowdown
    # bundle_path=r"models\dmax_predictor_2bundle_05262025.joblib" no longer using cause resources

    """
    Loads model bundle and predicts Dmax for row j of df.
    Returns the predicted Dmax and feature values used.
    The name of the model bundle must remain the same for it to work
    Need to path the actual bundle now instead of the path as this is loaded in the main script

    """
    try:
        # bundle = load(bundle_path)
        bundle = bundle_path  # load_model(bundle_path)
        model = bundle["model"]
        scaler = bundle["scaler"]
        feature_names = bundle["features"]

        # Mapping of model-trained features to your df column names
        feature_map = {
            "guinier_rg": "Final Rg",
            "V3 OG": "V_3",
            "V4 OG": "V_4",
            "V5 OG": "V_5",
            "min_qrg OG": "Final qRg min",
        }

        # Extract and scale feature vector
        feature_vector = np.array(
            [df.loc[df.index[j], feature_map[feat]] for feat in feature_names]
        ).reshape(1, -1)

        # feature_vector should be a 1D or 2D array (e.g., shape (1, n_features))
        # feature_names should be the exact names used during training
        scaled = scaler.transform(pd.DataFrame(feature_vector, columns=feature_names))

        prediction = model.predict(scaled)[0]

        # Return result + raw features used
        return prediction, {
            feat: df.loc[df.index[j], feature_map[feat]] for feat in feature_names
        }

    except Exception as e:
        logging.warning(f"Dmax prediction failed for index {j}: {e}")
        return np.nan, {"error": str(e)}


def assign_gmm_clusters(df, j, bundle_path=None):
    # "gmm_cluster_2bundle_05262025.joblib" --- Now passing as bundle in main script
    # bundle_path=r"models\gmm_cluster_2bundle_05262025.joblib" no longer using cause resources
    """
    Loads model bundle and predicts cluster probabilities using GMM for row j of df.
    Returns the predicted cluster and feature values used.
    The name of the model bundle must remain the same for it to work
    instead of a path now needs the model bundle passed
    """

    try:
        # bundle = load(bundle_path)
        bundle = bundle_path  # load_model(bundle_path)
        model = bundle["model"]
        scaler = bundle["scaler"]
        features = bundle["features"]

        # Map feature names
        feature_map = {"V3 OG": "V_3", "V4 OG": "V_4", "V5 OG": "V_5"}

        raw_feature_values = [df.loc[df.index[j], feature_map[ft]] for ft in features]
        scaled = scaler.transform([raw_feature_values])

        cluster = int(model.predict(scaled)[0])
        probs = model.predict_proba(scaled)[0]

        df.loc[df.index[j], "GMM Cluster"] = cluster
        for i, p in enumerate(probs):
            df.loc[df.index[j], f"Cluster Prob {i}"] = p

        return {
            "Cluster": cluster,
            "Probabilities": {f"Cluster {i}": float(p) for i, p in enumerate(probs)},
        }

    except Exception as e:
        logging.warning(f"GMM clustering failed for index {j}: {e}")
        return None


def get_franke_features2(q, rg, I_q, i0):
    """
    Getting features used for shape classification by Franke in Machine learning methods
    for X-ray scattering data analysis from biomacromolecular solutions
    """
    k_y = ((q * rg) ** 2) * I_q / i0
    k_x = q * rg
    # Find indx of qRg = 3, 4, 5
    ind_1_7, ind_3, ind_4, ind_5, ind_6, ind_7, ind_8 = (
        np.argmin(abs(k_x - 1.73)),
        np.argmin(abs(k_x - 3)),
        np.argmin(abs(k_x - 4)),
        np.argmin(abs(k_x - 5)),
        np.argmin(abs(k_x - 6)),
        np.argmin(abs(k_x - 7)),
        np.argmin(abs(k_x - 8)),
    )
    k_y_1_7, k_y_3, k_y_4, k_y_5, k_y_6, k_y_7, k_y_8 = (
        k_y[:ind_1_7],
        k_y[:ind_3],
        k_y[:ind_4],
        k_y[:ind_5],
        k_y[:ind_6],
        k_y[:ind_7],
        k_y[:ind_8],
    )
    k_x_1_7, k_x_3, k_x_4, k_x_5, k_x_6, k_x_7, k_x_8 = (
        k_x[:ind_1_7],
        k_x[:ind_3],
        k_x[:ind_4],
        k_x[:ind_5],
        k_x[:ind_6],
        k_x[:ind_7],
        k_x[:ind_8],
    )
    # find Q' (normalized porod invariant)
    Q_1_7, Q_3, Q_4, Q_5, Q_6, Q_7, Q_8 = (
        trapezoid(k_y_1_7, k_x_1_7),
        trapezoid(k_y_3, k_x_3),
        trapezoid(k_y_4, k_x_4),
        trapezoid(k_y_5, k_x_5),
        trapezoid(k_y_6, k_x_6),
        trapezoid(k_y_7, k_x_7),
        trapezoid(k_y_8, k_x_8),
    )
    V_1_7, V_3, V_4, V_5, V_6, V_7, V_8 = (
        (2 * np.pi**2) / Q_1_7,
        (2 * np.pi**2) / Q_3,
        (2 * np.pi**2) / Q_4,
        (2 * np.pi**2) / Q_5,
        (2 * np.pi**2) / Q_6,
        (2 * np.pi**2) / Q_7,
        (2 * np.pi**2) / Q_8,
    )

    return V_1_7, V_3, V_4, V_5, V_6, V_7, V_8
