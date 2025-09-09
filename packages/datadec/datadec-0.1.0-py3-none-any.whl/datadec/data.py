import itertools
from typing import List, Optional, Tuple, Union

import pandas as pd

from datadec import constants as consts
from datadec import data_utils, df_utils, model_utils, validation
from datadec.loader import DataFrameLoader
from datadec.paths import DataDecidePaths
from datadec.pipeline import DataPipeline, verbose_print

ID_COLUMNS = ["params", "data", "seed", "step", "tokens"]


class DataDecide:
    def __init__(
        self,
        data_dir: str = "./data",
        recompute_from: str = None,
        verbose: bool = True,
    ):
        self.paths = DataDecidePaths(data_dir)

        self.pipeline = DataPipeline(self.paths)
        self.pipeline.run(recompute_from=recompute_from, verbose=verbose)

        self.loader = DataFrameLoader(self.paths)
        self.loader.set_name(
            consts.MODEL_DETAILS_DF_NAME,
            model_utils.get_model_details_df(),
        )
        self.loader.set_name(
            consts.DATASET_DETAILS_DF_NAME,
            data_utils.get_data_recipe_details_df(self.paths.ds_details_csv_path),
        )
        verbose_print("Finished setting up DataDecide.", verbose)

    @property
    def all_data_param_combos(self):
        return list(
            itertools.product(
                consts.ALL_DATA_NAMES,
                consts.ALL_MODEL_SIZE_STRS,
            )
        )

    @property
    def full_eval(self) -> pd.DataFrame:
        return self.loader.load_name("full_eval")

    @property
    def mean_eval(self) -> pd.DataFrame:
        return self.loader.load_name("mean_eval")

    def load_dataframe(self, name: str) -> pd.DataFrame:
        return self.loader.load_name(name)

    def get_filtered_df(
        self,
        input_df: Optional[pd.DataFrame] = None,
        filter_types: List[str] = ["max_steps"],
        return_means: bool = True,
        min_params: str = "10M",
        verbose: bool = False,
    ) -> pd.DataFrame:
        base_df = input_df if input_df is not None else self.full_eval
        df = self.filter_data_quality(
            base_df, filter_types=filter_types, verbose=verbose
        )
        df = self.select_subset(df, min_params=min_params, verbose=verbose)
        if return_means:
            df = self.aggregate_results(df, by_seeds=True, verbose=verbose)
        return df

    def easy_index_df(
        self,
        input_df: Optional[pd.DataFrame] = None,
        df_name: str = "full_eval",
        data: Optional[Union[str, List[str]]] = None,
        params: Optional[Union[str, List[str]]] = None,
        seeds: Optional[Union[int, List[int]]] = None,
        step: Optional[Union[int, List[int]]] = None,
        data_param_combos: Optional[List[Tuple[str, str]]] = None,
        keep_cols: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        base_df = input_df if input_df is not None else self.load_dataframe(df_name)
        if step is not None:
            step_list = step if isinstance(step, list) else [step]
            base_df = base_df[base_df["step"].isin(step_list)]
        return self.select_subset(
            base_df,
            data=data,
            params=params,
            seeds=seeds,
            data_param_combos=data_param_combos,
            columns=keep_cols,
        )

    def aggregate_results(
        self,
        input_df: pd.DataFrame,
        by_seeds: bool = True,
        return_std: bool = False,
        verbose: bool = False,
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
        if len(input_df) == 0 or not by_seeds:
            df_utils.print_shape(input_df, "Empty DataFrame or no aggregation", verbose)
            if return_std:
                return input_df.copy(), input_df.copy()
            return input_df.copy()
        df_utils.print_shape(input_df, "Before aggregation", verbose)
        mean_df, std_df = df_utils.create_mean_std_df(input_df)
        df_utils.print_shape(mean_df, "After aggregation (means)", verbose)
        if return_std:
            df_utils.print_shape(std_df, "After aggregation (stds)", verbose)
            return mean_df, std_df
        return mean_df

    def filter_data_quality(
        self,
        input_df: pd.DataFrame,
        filter_types: List[str] = ["max_steps"],
        verbose: bool = False,
    ) -> pd.DataFrame:
        validation.validate_filter_types(filter_types)
        df = input_df.copy()
        df_utils.print_shape(df, "Initial", verbose)
        if len(df) == 0:
            df_utils.print_shape(df, "Empty DataFrame, no filtering", verbose)
            return df

        for filter_type in filter_types:
            if filter_type == "max_steps":
                df = df_utils.filter_by_max_step_to_use(df)
                df_utils.print_shape(df, "LEQ to max step", verbose)
            elif filter_type == "ppl":
                df = df_utils.filter_ppl_rows(df)
                df_utils.print_shape(df, "Non-NaN perplexity", verbose)
            elif filter_type == "olmes":
                df = df_utils.filter_olmes_rows(df)
                df_utils.print_shape(df, "Non-NaN OLMES", verbose)
        return df

    def select_subset(
        self,
        input_df: pd.DataFrame,
        data: Optional[Union[str, List[str]]] = None,
        params: Optional[Union[str, List[str]]] = None,
        seeds: Optional[Union[int, List[int]]] = None,
        step_lims: Optional[Tuple[Optional[int], Optional[int]]] = None,
        token_lims: Optional[Tuple[Optional[int], Optional[int]]] = None,
        min_params: Optional[str] = None,
        max_params: Optional[str] = None,
        data_param_combos: Optional[List[Tuple[str, str]]] = None,
        columns: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        metric_type: Optional[str] = None,
        include_id_columns: bool = True,
        verbose: bool = False,
    ) -> pd.DataFrame:
        df = input_df.copy()
        df_utils.print_shape(df, "Initial subset selection", verbose)
        if len(df) == 0:
            df_utils.print_shape(df, "Empty DataFrame, no selection", verbose)
            return df

        data = data if data is None else self.select_data(data)
        params = params if params is None else self.select_params(params)
        df = df_utils.select_by_data_param_combos(df, data, params, data_param_combos)
        df_utils.print_shape(df, "After data/param selection", verbose)

        if min_params is not None:
            min_params_numeric = (
                model_utils.param_to_numeric(min_params)
                if isinstance(min_params, str)
                else min_params
            )
            df = df[df[consts.PARAM_NUMERIC_COL] >= min_params_numeric]
            df_utils.print_shape(df, f"Above min params {min_params}", verbose)

        if max_params is not None:
            max_params_numeric = (
                model_utils.param_to_numeric(max_params)
                if isinstance(max_params, str)
                else max_params
            )
            df = df[df[consts.PARAM_NUMERIC_COL] <= max_params_numeric]
            df_utils.print_shape(df, f"Below max params {max_params}", verbose)

        if seeds is not None:
            seeds = seeds if isinstance(seeds, list) else [seeds]
            df = df[df["seed"].isin(seeds)]
            df_utils.print_shape(df, f"Seeds {seeds}", verbose)

        if step_lims is not None:
            min_step, max_step = step_lims
            if min_step is not None:
                df = df[df["step"] >= min_step]
            if max_step is not None:
                df = df[df["step"] <= max_step]
            df_utils.print_shape(df, f"Step range {step_lims}", verbose)

        if token_lims is not None:
            min_tokens, max_tokens = token_lims
            if min_tokens is not None:
                df = df[df["tokens"] >= min_tokens]
            if max_tokens is not None:
                df = df[df["tokens"] <= max_tokens]
            df_utils.print_shape(df, f"Token range {token_lims}", verbose)

        if columns or metrics or metric_type:
            selected_columns = self._build_column_list(
                df, columns, metrics, metric_type, include_id_columns
            )
            df = df[selected_columns]
            df_utils.print_shape(
                df, f"Selected {len(selected_columns)} columns", verbose
            )

        return df

    def _build_column_list(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]],
        metrics: Optional[List[str]],
        metric_type: Optional[str],
        include_id_columns: bool,
    ) -> List[str]:
        validation.validate_metric_type(metric_type)
        selected_columns = set()

        if include_id_columns:
            selected_columns.update(col for col in ID_COLUMNS if col in df.columns)

        if columns:
            selected_columns.update(col for col in columns if col in df.columns)

        if metric_type and metric_type == "ppl":
            selected_columns.update(
                col for col in consts.PPL_TYPES if col in df.columns
            )
        elif metric_type and metric_type == "olmes":
            selected_columns.update(
                col for col in consts.OLMES_TASKS if col in df.columns
            )
        if metrics:
            validation.validate_metrics(metrics)
            selected_columns.update(
                metric for metric in metrics if metric in df.columns
            )
        if not selected_columns:
            selected_columns = list(df.columns)
        return list(selected_columns)

    def select_params(
        self,
        params: Union[str, List[str]] = "all",
        exclude: Optional[List[str]] = None,
    ) -> List[str]:
        return validation._validated_select(
            choices=params,
            valid_options=consts.ALL_MODEL_SIZE_STRS,
            name="parameter size",
            exclude=exclude,
        )

    def select_data(
        self,
        data: Union[str, List[str]] = "all",
        exclude: Optional[List[str]] = None,
    ) -> List[str]:
        return validation._validated_select(
            choices=data,
            valid_options=consts.ALL_DATA_NAMES,
            name="data recipe",
            exclude=exclude,
        )

    def melt_for_plotting(
        self,
        df: pd.DataFrame,
        metrics: Optional[List[str]] = None,
        include_seeds: bool = True,
        drop_na: bool = True,
    ) -> pd.DataFrame:
        if metrics is None:
            metrics = [col for col in df.columns if col in consts.ALL_KNOWN_METRICS]

        id_cols = (
            ID_COLUMNS
            if include_seeds
            else [col for col in ID_COLUMNS if col != "seed"]
        )
        available_id_cols = [col for col in id_cols if col in df.columns]

        melted_df = df.melt(
            id_vars=available_id_cols,
            value_vars=metrics,
            var_name="metric",
            value_name="value",
        )

        if drop_na:
            melted_df = melted_df.dropna(subset=["value"])

        return melted_df

    def prepare_plot_data(
        self,
        params: Optional[Union[str, List[str]]] = None,
        data: Optional[Union[str, List[str]]] = None,
        metrics: Optional[List[str]] = None,
        aggregate_seeds: bool = False,
        input_df: Optional[pd.DataFrame] = None,
        auto_filter: bool = True,
        melt: bool = True,
        verbose: bool = False,
        **select_subset_kwargs,
    ) -> pd.DataFrame:
        base_df = input_df if input_df is not None else self.full_eval

        if auto_filter and metrics:
            filter_types = validation.determine_filter_types(metrics)
            df = self.filter_data_quality(
                base_df, filter_types=filter_types, verbose=verbose
            )
        else:
            df = base_df.copy()

        df = self.select_subset(
            df,
            params=params,
            data=data,
            metrics=metrics,
            verbose=verbose,
            **select_subset_kwargs,
        )

        if aggregate_seeds:
            df = self.aggregate_results(df, by_seeds=True, verbose=verbose)

        if melt:
            return self.melt_for_plotting(
                df, metrics=metrics, include_seeds=not aggregate_seeds
            )
        return df
