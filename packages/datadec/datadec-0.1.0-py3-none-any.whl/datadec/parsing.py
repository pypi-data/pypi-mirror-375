from typing import List, Optional

import orjson
import pandas as pd

from datadec import constants as consts
from datadec import model_utils


def reorder_df_cols(df: pd.DataFrame, prefix_order: List[str]) -> pd.DataFrame:
    df = df.copy()
    return df[prefix_order + [col for col in df.columns if col not in prefix_order]]


def map_seed_col_to_int(df: pd.DataFrame) -> pd.DataFrame:
    df["seed"] = df["seed"].map(consts.SEED_MAP)
    return df


# --------- Step to Token/Compute Parsing ---------


def make_step_to_token_compute_df(dwn_df: pd.DataFrame) -> pd.DataFrame:
    assert all([c in dwn_df.columns for c in consts.STEP_TOK_COMP_COLS])
    base_map = dwn_df[consts.STEP_TOK_COMP_COLS].groupby("params").max().reset_index()
    step_map = base_map[["params"]].copy()
    step_map["tokens_per_step"] = base_map["tokens"] / base_map["step"]
    step_map["compute_per_step"] = base_map["compute"] / base_map["step"]
    return step_map


def merge_in_step_to_token_compute_df(
    base_df: pd.DataFrame,
    step_to_token_compute_df: pd.DataFrame,
) -> pd.DataFrame:
    return (
        base_df.merge(step_to_token_compute_df, on="params", how="left")
        .assign(
            tokens=lambda x: x["step"] * x["tokens_per_step"],
            compute=lambda x: x["step"] * x["compute_per_step"],
        )
        .drop(columns=["tokens_per_step", "compute_per_step"])
    )


def make_and_merge_step_to_token_compute_df(
    dwn_df: pd.DataFrame,
    base_df: pd.DataFrame,
) -> pd.DataFrame:
    step_to_token_compute_df = make_step_to_token_compute_df(dwn_df)
    return merge_in_step_to_token_compute_df(base_df, step_to_token_compute_df)


# --------- Downstream Metric Parsing Helpers ---------


def list_col_to_columns(orig_df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    df = orig_df.copy()
    json_data = df[col_name].str.replace("'", '"')
    parsed_data = [orjson.loads(item) for item in json_data]
    json_data_df = pd.json_normalize(parsed_data)

    df = pd.concat([df.drop(col_name, axis=1), json_data_df], axis=1)
    return df


def average_mmlu_metrics(df: pd.DataFrame) -> pd.DataFrame:
    assert (
        "task" in df.columns
        and "mmlu_average" not in df.columns
        and "mmlu_average_correct_prob" not in df.columns
    )
    mmlu_df = df[df["task"].isin(consts.MMLU_TASKS)].drop(columns=["task"])
    mmlu_avg = mmlu_df.groupby(consts.KEY_COLS).agg("mean").reset_index()
    mmlu_avg["task"] = "mmlu_average"
    return pd.concat([df, mmlu_avg], ignore_index=True)


def pivot_task_metrics_to_columns(dwn_df: pd.DataFrame) -> pd.DataFrame:
    pivoted_metrics = []
    for metric_col in consts.METRIC_NAMES:
        pivoted = dwn_df.pivot_table(
            index=consts.KEY_COLS,
            columns="task",
            values=metric_col,
            aggfunc="first",
        )
        pivoted.columns = [f"{task}_{metric_col}" for task in pivoted.columns]
        pivoted_metrics.append(pivoted)
    return pd.concat(pivoted_metrics, axis=1).reset_index()


def parse_downstream_expanded_df(dwn_df_raw: pd.DataFrame) -> pd.DataFrame:
    # list_col_to_columns should have been called before this
    assert "metrics" not in dwn_df_raw.columns and "task" in dwn_df_raw.columns
    df = dwn_df_raw.copy()
    df = df.drop(columns=consts.DWN_DROP_COLS + consts.DROP_METRICS, errors="ignore")
    df = average_mmlu_metrics(df)
    df = pivot_task_metrics_to_columns(df)
    df = reorder_df_cols(df, prefix_order=consts.KEY_COLS)
    df = map_seed_col_to_int(df)
    return df


# --------- Perplexity Metric Parsing ---------
def parse_perplexity_df(ppl_df_raw: pd.DataFrame) -> pd.DataFrame:
    df = ppl_df_raw.copy()
    df = df.drop(columns=consts.PPL_DROP_COLS, errors="ignore")
    df = df.rename(columns=consts.PPL_NAME_MAP)
    df = reorder_df_cols(df, prefix_order=consts.KEY_COLS)
    df = map_seed_col_to_int(df)
    return df


# --------- Merge Helpers ---------
def merge_all_dfs(
    dwn_raw_df: pd.DataFrame,
    ppl_parsed_df: pd.DataFrame,
    dwn_parsed_df: pd.DataFrame,
    dataset_details_df: Optional[pd.DataFrame] = None,
    model_details_df: Optional[pd.DataFrame] = None,
    add_token_compute: bool = True,
) -> pd.DataFrame:
    df = pd.merge(ppl_parsed_df, dwn_parsed_df, on=consts.KEY_COLS, how="outer")

    if add_token_compute:
        df = make_and_merge_step_to_token_compute_df(dwn_raw_df, df)

    if dataset_details_df is not None:
        df = df.merge(dataset_details_df, on="data", how="left")

    if model_details_df is not None:
        df = df.merge(model_details_df, on="params", how="left")

    return reorder_df_cols(df, prefix_order=consts.FINAL_PREFIX_COLS)


# --------- LR Helpers ---------
def add_lr_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df_by_params = df[["params"] + consts.LR_INPUT_COLS]
    df_by_params = df_by_params.groupby(["params", "step"]).first().reset_index()
    lr_fxns = {
        "lr_at_step": model_utils.get_lr_at_step,
        "cumulative_lr": model_utils.calculate_cumulative_lr,
    }
    for col_name, fxn in lr_fxns.items():
        df_by_params[col_name] = df_by_params.apply(
            lambda row: fxn(**{k: row[k] for k in consts.LR_INPUT_COLS}),
            axis=1,
        )
    df_by_params = df_by_params[["params", "step"] + consts.LR_OUTPUT_COLS]
    df = df.merge(df_by_params, on=["params", "step"], how="left")
    return reorder_df_cols(
        df, prefix_order=consts.FINAL_PREFIX_COLS + consts.LR_OUTPUT_COLS
    )
