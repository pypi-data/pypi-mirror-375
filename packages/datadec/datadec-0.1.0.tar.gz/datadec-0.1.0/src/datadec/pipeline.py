from pathlib import Path
from typing import Optional

import pandas as pd
from datasets import load_dataset

from datadec import constants as consts
from datadec import data_utils, df_utils, model_utils, parsing
from datadec.paths import DataDecidePaths


def download_dataset(
    path: Path,
    repo_id: str,
    split: str,
) -> None:
    raw_df = load_dataset(repo_id, split=split)
    raw_df.to_parquet(path)


def verbose_print(msg: str, verbose: bool = False) -> None:
    if verbose:
        print(f">> {msg}")


class DataPipeline:
    def __init__(self, paths: DataDecidePaths):
        self.paths = paths
        self.pipeline_stage_fxns = {
            "download": self.download_raw_data,
            "metrics_expand": self.expand_dwn_metrics_column,
            "parse": self.parse_datasets,
            "merge": self.merge_datasets,
            "enrich": self.enrich_dataset,
            "aggregate": self.create_aggregated_datasets,
        }

        self.stage_outputs = {
            "download": ["ppl_raw", "dwn_raw"],
            "metrics_expand": ["dwn_metrics_expanded"],
            "parse": ["ppl_parsed", "dwn_parsed"],
            "merge": ["full_eval_raw"],
            "enrich": ["full_eval"],
            "aggregate": ["mean_eval", "std_eval"],
        }

    def usage_info(self) -> None:
        print("Available stages:")
        for stage_name in self.pipeline_stage_fxns.keys():
            print(f"- {stage_name}")
        print("\n Use: `pipeline.run_stage('stage_name')` to run a stage")

    def run_stage(self, stage_name: str, verbose: bool = False) -> None:
        verbose_print(f" --- Running {stage_name} stage ---", verbose)
        self.pipeline_stage_fxns[stage_name](verbose=verbose)

    def download_raw_data(self, verbose: bool = False) -> None:
        for raw_metric_type in ["ppl", "dwn"]:
            verbose_print(f"Downloading {raw_metric_type} raw data", verbose)
            download_path = self.paths.get_path(f"{raw_metric_type}_raw")
            download_dataset(
                path=download_path,
                repo_id=consts.HF_DATASET_NAMES[f"{raw_metric_type}_eval_ds"],
                split=consts.HF_DATASET_SPLIT,
            )
            verbose_print(f"Wrote to {download_path}", verbose)

    def expand_dwn_metrics_column(self, verbose: bool = False) -> None:
        verbose_print("Expanding downstream metrics column", verbose)
        dwn_df = pd.read_parquet(self.paths.get_path("dwn_raw"))
        expanded_df = parsing.list_col_to_columns(dwn_df, "metrics")
        expanded_path = self.paths.get_path("dwn_metrics_expanded")
        expanded_df.to_parquet(expanded_path)
        verbose_print(f"Wrote to {expanded_path}", verbose)

    def parse_datasets(self, verbose: bool = False) -> None:
        verbose_print("Downstream DF Parsing", verbose)
        dwn_expanded = pd.read_parquet(self.paths.get_path("dwn_metrics_expanded"))
        dwn_parsed = parsing.parse_downstream_expanded_df(dwn_expanded)
        dwn_parsed_path = self.paths.get_path("dwn_parsed")
        dwn_parsed.to_parquet(dwn_parsed_path)
        verbose_print(f"Wrote to {dwn_parsed_path}", verbose)

        verbose_print("Perplexity DF Parsing", verbose)
        ppl_df = pd.read_parquet(self.paths.get_path("ppl_raw"))
        ppl_parsed = parsing.parse_perplexity_df(ppl_df)
        ppl_parsed_path = self.paths.get_path("ppl_parsed")
        ppl_parsed.to_parquet(ppl_parsed_path)
        verbose_print(f"Wrote to {ppl_parsed_path}", verbose)

    def merge_datasets(self, verbose: bool = False) -> None:
        verbose_print("Merging ppl, dwn, dataset and model detail dfs", verbose)
        full_eval_raw = parsing.merge_all_dfs(
            dwn_raw_df=pd.read_parquet(self.paths.get_path("dwn_raw")),
            ppl_parsed_df=pd.read_parquet(self.paths.get_path("ppl_parsed")),
            dwn_parsed_df=pd.read_parquet(self.paths.get_path("dwn_parsed")),
            dataset_details_df=data_utils.get_data_recipe_details_df(
                self.paths.ds_details_csv_path
            ),
            model_details_df=model_utils.get_model_details_df(),
            add_token_compute=True,
        )
        full_eval_raw_path = self.paths.get_path("full_eval_raw")
        full_eval_raw.to_parquet(full_eval_raw_path)
        verbose_print(f"Wrote to {full_eval_raw_path}", verbose)

    def enrich_dataset(self, verbose: bool = False) -> None:
        verbose_print("Enriching dataset", verbose)
        df = pd.read_parquet(self.paths.get_path("full_eval_raw"))
        df = parsing.add_lr_cols(df)
        full_eval_path = self.paths.get_path("full_eval")
        df.to_parquet(full_eval_path)
        verbose_print(f"Wrote to {full_eval_path}", verbose)

    def create_aggregated_datasets(self, verbose: bool = False) -> None:
        verbose_print("Creating mean and standard deviation datasets", verbose)
        full_eval_df = pd.read_parquet(self.paths.get_path("full_eval"))
        mean_df, std_df = df_utils.create_mean_std_df(full_eval_df)
        mean_df_path = self.paths.get_path("mean_eval")
        mean_df.to_parquet(mean_df_path)
        verbose_print(f"Wrote to {mean_df_path}", verbose)
        std_df_path = self.paths.get_path("std_eval")
        std_df.to_parquet(std_df_path)
        verbose_print(f"Wrote to {std_df_path}", verbose)

    def run(self, recompute_from: Optional[str] = None, verbose: bool = False) -> None:
        recompute_from = "download" if recompute_from == "all" else recompute_from
        compute_all = False
        for stage_name, stage_fxn in self.pipeline_stage_fxns.items():
            expected_output_exists = [
                self.paths.get_path(out).exists()
                for out in self.stage_outputs[stage_name]
            ]
            missing_output = not all(expected_output_exists)
            if compute_all or missing_output or recompute_from == stage_name:
                compute_all = True
                self.run_stage(stage_name, verbose=verbose)
