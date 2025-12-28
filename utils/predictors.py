import numpy as np
import pandas as pd
from typing import Tuple, Dict


def _infer_target_column(df: pd.DataFrame) -> str:
    """
    Very naive heuristic:
    - If a column named 'target' exists, use that
    - Else, use the last numeric column
    - Else, use the last column
    """
    if "target" in df.columns:
        return "target"

    numeric_cols = df.select_dtypes(include=["number"]).columns
    if len(numeric_cols) > 0:
        return numeric_cols[-1]

    return df.columns[-1]


def _auto_detect_task(df: pd.DataFrame, target_col: str) -> str:
    """
    Simple auto-detection:
    - If target has <= 10 unique values and is not numeric → classification
    - If target is numeric → regression
    - Fallback → clustering
    """
    y = df[target_col]
    if y.dtype == "object" or y.dtype.name == "category":
        if y.nunique() <= 10:
            return "Classification"
        else:
            return "Clustering"
    else:
        if y.nunique() <= 10 and y.nunique() / len(y) < 0.5:
            return "Classification"
        else:
            return "Regression"


def run_predictive_pipeline(
    df: pd.DataFrame,
    task_type: str = "Auto-detect"
) -> Tuple[pd.DataFrame, Dict]:
    """
    Returns:
      - prediction_result: DataFrame
      - model_info: dict
    """
    df = df.copy()

    # Choose target
    target_col = _infer_target_column(df)
    if task_type == "Auto-detect":
        task_type = _auto_detect_task(df, target_col)

    X = df.drop(columns=[target_col], errors="ignore")
    y = df[target_col] if target_col in df.columns else None

    # For novices: we use very simple models
    if task_type == "Regression":
        result_df = _simple_regression(X, y)
    elif task_type == "Classification":
        result_df = _simple_classification(X, y)
    else:
        result_df = _simple_clustering(X)

    model_info = {
        "task_type": task_type,
        "target_column": target_col if target_col in df.columns else None,
        "row_count": len(df),
        "feature_columns": list(X.columns),
        "note": "This is a simple heuristic model for demo purposes. Easily replace with real models."
    }

    return result_df, model_info


def _simple_regression(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """
    For demo: predict using a trivial baseline:
    - y_pred = mean(y)
    """
    if y is None:
        baseline = 0
    else:
        baseline = float(y.mean())

    result = X.copy()
    result["prediction"] = baseline
    return result


def _simple_classification(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """
    For demo: predict the most frequent class.
    """
    if y is None:
        most_freq = "class_0"
    else:
        most_freq = y.mode().iloc[0]

    result = X.copy()
    result["prediction"] = most_freq
    return result


def _simple_clustering(X: pd.DataFrame, n_clusters: int = 3) -> pd.DataFrame:
    """
    For demo: assign pseudo-clusters at random.
    You can replace this with KMeans or other clustering algorithms.
    """
    result = X.copy()
    if len(X) == 0:
        result["cluster"] = []
        return result

    result["cluster"] = np.random.randint(0, n_clusters, size=len(X))
    return result