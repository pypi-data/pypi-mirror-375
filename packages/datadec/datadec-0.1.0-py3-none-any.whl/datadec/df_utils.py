from typing import List, Optional, Tuple

import pandas as pd

from datadec import constants as consts


def print_shape(df: pd.DataFrame, msg: str = "", verbose: bool = False):
    if verbose:
        print(f"{msg} shape: {df.shape[0]:,} rows x {df.shape[1]:,} cols")


def filter_by_max_step_to_use(df: pd.DataFrame) -> pd.DataFrame:
    max_step_filter = df["params"].map(consts.MAX_STEP_TO_USE)
    return df[df["step"] <= max_step_filter]


def filter_ppl_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out rows where all perplexity columns have NaN values."""
    ppl_columns = [col for col in df.columns if col in consts.PPL_TYPES]
    assert len(ppl_columns) > 0, (
        f"No perplexity columns found in dataframe. Expected: {consts.PPL_TYPES}"
    )

    initial_count = len(df)
    filtered_df = df.dropna(subset=ppl_columns, how="all")
    removed_count = initial_count - len(filtered_df)

    if removed_count > 0:
        print(f"Filtered out {removed_count} rows with all NaN perplexity values")

    return filtered_df


def filter_olmes_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out rows where all OLMES metric columns have NaN values."""
    olmes_columns = [
        col for col in df.columns if any(task in col for task in consts.OLMES_TASKS)
    ]
    assert len(olmes_columns) > 0, (
        f"No OLMES metric columns found in dataframe. Expected tasks: {consts.OLMES_TASKS}"
    )

    initial_count = len(df)
    filtered_df = df.dropna(subset=olmes_columns, how="all")
    removed_count = initial_count - len(filtered_df)

    if removed_count > 0:
        print(f"Filtered out {removed_count} rows with all NaN OLMES metric values")

    return filtered_df


def select_by_data_param_combos(
    df: pd.DataFrame,
    data: Optional[List[str]] = None,
    params: Optional[List[str]] = None,
    data_param_combos: Optional[List[Tuple[str, str]]] = None,
) -> pd.DataFrame:
    data = data or consts.ALL_DATA_NAMES
    params = params or consts.ALL_MODEL_SIZE_STRS

    if data_param_combos:
        combined_filter = pd.Series([False] * len(df), index=df.index)
        for data_name, param_name in data_param_combos:
            combo_filter = (df["data"] == data_name) & (df["params"] == param_name)
            combined_filter = combined_filter | combo_filter
        return df[combined_filter]
    return df[df["data"].isin(data) & df["params"].isin(params)]


def create_mean_std_df(merged_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    group_cols = ["params", "data", "step"]
    exclude_cols = group_cols + ["seed"]  # Exclude seed from aggregation

    numeric_cols = merged_df.select_dtypes(include=["number"]).columns.tolist()
    agg_cols = [col for col in numeric_cols if col not in exclude_cols]

    mean_df = merged_df.groupby(group_cols)[agg_cols].mean().reset_index()
    std_df = merged_df.groupby(group_cols)[agg_cols].std().reset_index()

    return mean_df, std_df
