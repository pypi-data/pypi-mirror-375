#!/usr/bin/env python3

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import ticker

from datadec import DataDecide
from datadec.constants import (
    BASE_AND_QC,
    BASE_RECIPES,
    CUSTOM_RECIPE_FAMILIES,
    OLMES_PERFORMANCE_RECIPE_CHUNKS,
    PPL_PERFORMANCE_RECIPE_CHUNKS,
    RECIPES_WITHOUT_ABLATIONS,
)
from dr_plotter import FigureManager
from dr_plotter.configs import PlotConfig
from dr_plotter.theme import BUMP_PLOT_THEME, Theme

# Formatting constants
THOUSAND = 1000
MILLION = 1e6
BILLION = 1e9

# Minimum data points for analysis
MIN_POINTS_FOR_SAMPLING = 2


def format_perplexity(ppl_value: float) -> str:
    return f"{ppl_value:.2f}"


def create_extended_color_palette() -> list[str]:
    return [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
        "#aec7e8",
        "#ffbb78",
        "#98df8a",
        "#ff9896",
        "#c5b0d5",
        "#c49c94",
        "#f7b6d3",
        "#c7c7c7",
        "#dbdb8d",
        "#9edae5",
        "#393b79",
        "#637939",
        "#8c6d31",
        "#843c39",
        "#7b4173",
        "#5254a3",
        "#8ca252",
        "#bd9e39",
        "#ad494a",
        "#a55194",
        "#6b6ecf",
        "#b5cf6b",
        "#e7ba52",
        "#d6616b",
        "#ce6dbd",
        "#de9ed6",
        "#31a354",
        "#756bb1",
        "#636363",
        "#969696",
    ]


def create_bump_theme_with_colors(num_categories: int) -> Theme:
    import itertools

    from dr_plotter import consts

    extended_colors = create_extended_color_palette()
    colors_to_use = extended_colors[: max(num_categories, len(extended_colors))]

    return Theme(
        name="bump_timesteps_extended",
        parent=BUMP_PLOT_THEME,
        **{
            consts.get_cycle_key("hue"): itertools.cycle(colors_to_use),
        },
    )


def format_step_label(step: float) -> str:
    if step >= THOUSAND:
        return f"{step / THOUSAND:.1f}k"
    else:
        return f"{int(step)}"


def format_token_count(token_count: float) -> str:
    if token_count >= BILLION:
        return f"{token_count / BILLION:.1f}B"
    elif token_count >= MILLION:
        return f"{token_count / MILLION:.0f}M"
    elif token_count >= THOUSAND:
        return f"{token_count / THOUSAND:.0f}K"
    else:
        return f"{int(token_count)}"


def downsample_timesteps(
    bump_data: pd.DataFrame, max_points: int, common_start_x: int | None = None
) -> pd.DataFrame:
    all_time_points = sorted(bump_data["time"].unique())

    if common_start_x is not None:
        time_points = [t for t in all_time_points if t >= common_start_x]
    else:
        time_points = all_time_points

    if len(time_points) <= max_points:
        if common_start_x is not None:
            return bump_data[bump_data["time"] >= common_start_x].copy()
        else:
            return bump_data

    if max_points < MIN_POINTS_FOR_SAMPLING:
        raise ValueError(
            "max_points must be at least 2 to preserve first and last points"
        )

    # Always keep first and last points
    selected_times = [time_points[0], time_points[-1]]

    # If we need more than just first and last, sample middle points
    if max_points > MIN_POINTS_FOR_SAMPLING:
        middle_points_needed = max_points - MIN_POINTS_FOR_SAMPLING
        middle_time_points = time_points[1:-1]  # Exclude first and last

        if middle_points_needed >= len(middle_time_points):
            # If we need more middle points than available, take all middle points
            selected_times.extend(middle_time_points)
        else:
            # Sample evenly spaced middle points
            indices = [
                int(i * len(middle_time_points) / (middle_points_needed + 1))
                for i in range(1, middle_points_needed + 1)
            ]
            selected_middle = [middle_time_points[i] for i in indices]
            selected_times.extend(selected_middle)

    # Sort selected times and filter data
    selected_times = sorted(set(selected_times))
    downsampled_data = bump_data[bump_data["time"].isin(selected_times)].copy()

    return downsampled_data


def get_model_size_color_scheme(categories: list[str]) -> dict[str, str]:
    model_sizes = []
    for cat in categories:
        # Extract model size from category (e.g., "150M-C4" -> "150M")
        model_size = cat.split("-")[0]
        model_sizes.append(model_size)

    # Sort by numeric value for proper progression
    from datadec.model_utils import param_to_numeric

    sorted_sizes = sorted(set(model_sizes), key=param_to_numeric)

    # Distinct colors for different model sizes
    distinct_colors = [
        "#FF6B6B",  # Bright red
        "#4ECDC4",  # Teal
        "#45B7D1",  # Blue
        "#96CEB4",  # Light green
        "#FFEAA7",  # Yellow
        "#DDA0DD",  # Plum
        "#FF8C69",  # Salmon
        "#98FB98",  # Pale green
        "#87CEEB",  # Sky blue
        "#F0E68C",  # Khaki
        "#FFB6C1",  # Light pink
        "#20B2AA",  # Light sea green
        "#FFA07A",  # Light salmon
        "#B0E0E6",  # Powder blue
    ]

    # Assign colors to model sizes
    size_to_color = {}
    for i, size in enumerate(sorted_sizes):
        size_to_color[size] = distinct_colors[i % len(distinct_colors)]

    return size_to_color


def downsample_per_trajectory(bump_data: pd.DataFrame, max_points: int) -> pd.DataFrame:
    if max_points < MIN_POINTS_FOR_SAMPLING:
        raise ValueError(
            "max_points must be at least 2 to preserve first and last points"
        )

    downsampled_trajectories = []

    for category in bump_data["category"].unique():
        trajectory_data = bump_data[bump_data["category"] == category].copy()
        trajectory_data = trajectory_data.sort_values("time")

        # Separate original vs interpolated points
        original_data = trajectory_data[~trajectory_data["is_interpolated"]].copy()
        interpolated_data = trajectory_data[trajectory_data["is_interpolated"]].copy()

        original_times = (
            sorted(original_data["time"].unique()) if not original_data.empty else []
        )

        # If we have few enough original points, use them all plus interpolated
        # as needed
        if len(original_times) <= max_points:
            selected_times = set(original_times)

            # Fill remaining slots with interpolated points if needed
            if len(selected_times) < max_points and not interpolated_data.empty:
                all_times = sorted(trajectory_data["time"].unique())
                remaining_times = [t for t in all_times if t not in selected_times]

                if remaining_times:
                    points_needed = max_points - len(selected_times)
                    if points_needed >= len(remaining_times):
                        selected_times.update(remaining_times)
                    else:
                        # Sample evenly from remaining interpolated points
                        indices = [
                            int(i * len(remaining_times) / (points_needed + 1))
                            for i in range(1, points_needed + 1)
                        ]
                        selected_interpolated = [remaining_times[i] for i in indices]
                        selected_times.update(selected_interpolated)
        else:
            # Too many original points, downsample them using original algorithm
            selected_times = [
                original_times[0],
                original_times[-1],
            ]  # Keep first/last original

            if max_points > MIN_POINTS_FOR_SAMPLING:
                middle_points_needed = max_points - MIN_POINTS_FOR_SAMPLING
                middle_original_times = original_times[1:-1]

                if middle_points_needed >= len(middle_original_times):
                    selected_times.extend(middle_original_times)
                else:
                    indices = [
                        int(i * len(middle_original_times) / (middle_points_needed + 1))
                        for i in range(1, middle_points_needed + 1)
                    ]
                    selected_middle = [middle_original_times[i] for i in indices]
                    selected_times.extend(selected_middle)

            selected_times = set(selected_times)

        # Filter trajectory data to selected times
        downsampled_trajectory = trajectory_data[
            trajectory_data["time"].isin(selected_times)
        ].copy()
        downsampled_trajectories.append(downsampled_trajectory)

    # Combine all downsampled trajectories
    return pd.concat(downsampled_trajectories, ignore_index=True)


def add_start_final_rank_labels(
    ax: plt.Axes,
    bump_data: pd.DataFrame,
    time_to_x: dict[float, float],
    offset_x: int = 50,
    offset_y: int = 8,
) -> None:
    time_points = sorted(bump_data["time"].unique())

    if len(time_points) < MIN_POINTS_FOR_SAMPLING:
        return  # Need at least 2 time points for start/final comparison

    first_time = time_points[0]
    last_time = time_points[-1]

    # Rank data at both time points
    ranked_data = []
    for time_point in [first_time, last_time]:
        time_data = bump_data[bump_data["time"] == time_point].copy()
        time_data = time_data.sort_values("score", ascending=False)
        time_data["rank"] = range(1, len(time_data) + 1)
        ranked_data.append(time_data)

    first_data, last_data = ranked_data

    # Create lookup dict for start ranks
    first_ranks = dict(zip(first_data["category"], first_data["rank"]))

    # Get color scheme for model sizes
    categories = sorted(last_data["category"].unique())
    size_to_color = get_model_size_color_scheme(categories)

    # Add Start/Final labels next to the last point for each category
    for _, row in last_data.iterrows():
        category = row["category"]
        start_rank = first_ranks.get(category, "?")
        final_rank = row["rank"]

        # Extract model size and get its color
        model_size = category.split("-")[0]
        color = size_to_color.get(model_size, "#90EE90")  # fallback to light green

        label_text = f"Start: {start_rank} Final: {final_rank}"

        ax.annotate(
            label_text,
            xy=(time_to_x[last_time], final_rank),
            xytext=(offset_x, offset_y),
            textcoords="offset points",
            fontsize=7,
            ha="left",
            va="bottom",
            bbox={
                "boxstyle": "round,pad=0.2",
                "facecolor": color,
                "alpha": 0.8,
                "edgecolor": "black",
            },
            arrowprops=None,
        )


def add_left_ranking_labels(ax: plt.Axes, bump_data: pd.DataFrame) -> None:
    time_points = sorted(bump_data["time"].unique())
    first_time = time_points[0]
    first_time_data = bump_data[bump_data["time"] == first_time].copy()
    first_time_data = first_time_data.sort_values("score", ascending=False)
    first_time_data["rank"] = range(1, len(first_time_data) + 1)

    # Get color scheme for model sizes
    categories = sorted(first_time_data["category"].unique())
    size_to_color = get_model_size_color_scheme(categories)

    for _, row in first_time_data.iterrows():
        category_name = row["category"]
        rank = row["rank"]

        # Extract model size and get its color
        model_size = category_name.split("-")[0]
        color = size_to_color.get(model_size, "#ADD8E6")  # fallback to light blue

        ax.text(
            -0.02,
            rank,
            f"{rank}. {category_name}",
            transform=ax.get_yaxis_transform(),
            fontsize=9,
            ha="right",
            va="center",
            fontweight="bold",
            bbox={
                "boxstyle": "round,pad=0.3",
                "facecolor": color,
                "alpha": 0.8,
                "edgecolor": "black",
            },
        )


def add_value_annotations(
    ax: plt.Axes,
    bump_data: pd.DataFrame,
    first_last_only: bool = False,
    label_time_points: set[float] | None = None,
    show_rank_labels: bool = False,
) -> None:
    time_points = sorted(bump_data["time"].unique())
    time_to_x = {time_point: time_point for time_point in time_points}

    ranked_data = []
    for time_point in time_points:
        time_data = bump_data[bump_data["time"] == time_point].copy()
        time_data = time_data.sort_values("score", ascending=False)
        time_data["rank"] = range(1, len(time_data) + 1)
        ranked_data.append(time_data)

    all_ranked_data = pd.concat(ranked_data, ignore_index=True)

    for _, row in all_ranked_data.iterrows():
        x_pos = time_to_x[row["time"]]
        y_pos = row["rank"]

        # If label_time_points is provided, only label those specific points
        if label_time_points is not None:
            if row["time"] not in label_time_points:
                continue
            # Even if in label_time_points, skip if this is an interpolated point
            # for this trajectory
            if row.get("is_interpolated", False):
                continue
        # Original logic: skip value labels for interpolated points
        # (unless in first-last-only mode)
        elif row.get("is_interpolated", False) and not first_last_only:
            continue

        # Only show labels for original data points
        ppl_text = format_perplexity(row["original_ppl"])

        ax.annotate(
            ppl_text,
            xy=(x_pos, y_pos),
            xytext=(5, 8),
            textcoords="offset points",
            fontsize=8,
            ha="left",
            va="bottom",
            bbox={
                "boxstyle": "round,pad=0.2",
                "facecolor": "white",
                "alpha": 0.8,
                "edgecolor": "gray",
            },
            arrowprops=None,
        )

    # Add Start/Final rank labels when requested
    if first_last_only or show_rank_labels:
        add_start_final_rank_labels(ax, bump_data, time_to_x)


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot bump chart rankings across training steps",
    )

    parser.add_argument(
        "metric",
        default="pile-valppl",
        nargs="?",
        help="Metric to plot for ranking comparison (default: pile-valppl)",
    )

    parser.add_argument(
        "--params",
        nargs="+",
        default=["all"],
        help="Model parameter sizes (e.g., 150M 300M 1B) or 'all' (default: all)",
    )

    parser.add_argument(
        "--data",
        nargs="+",
        default=["all"],
        help="Data recipes: 'all', 'base', 'base_qc', 'no_ablations',"
        " or specific names. Named groups: 'core_datasets', 'dolma17_variants',"
        " 'dclm_variants', 'falcon_cc_variants', 'fineweb_variants', "
        "'mix_with_baselines', 'best_ppl', 'good_ppl', 'medium_ppl', 'poor_ppl',"
        " 'best_olmes', 'good_olmes', 'medium_olmes', 'poor_olmes'",
    )

    parser.add_argument(
        "--exclude-data",
        nargs="+",
        default=[],
        help="Data recipes to exclude when using 'all'",
    )

    parser.add_argument("--save", type=str, help="Save plot to file (specify path)")
    parser.add_argument(
        "--no-show", action="store_true", help="Don't display plot interactively"
    )

    parser.add_argument(
        "--figsize",
        nargs=2,
        type=float,
        default=[14, 8],
        help="Figure size width height (default: 14 8)",
    )

    parser.add_argument(
        "--width-per-point",
        type=float,
        default=0.8,
        help="Width scaling factor per time point (default: 0.8)",
    )

    parser.add_argument(
        "--height-per-line",
        type=float,
        default=0.15,
        help="Height scaling factor per trajectory line (default: 0.15)",
    )

    parser.add_argument(
        "--min-step",
        type=float,
        help="Minimum training step to include (optional)",
    )

    parser.add_argument(
        "--max-step",
        type=float,
        help="Maximum training step to include (optional)",
    )

    parser.add_argument(
        "--first-last-only",
        action="store_true",
        help="Show only first and last rankings (compressed view)",
    )

    parser.add_argument(
        "--interpolate",
        action="store_true",
        help="Use linear interpolation for missing timestep data ",
    )

    parser.add_argument(
        "--max-points",
        type=int,
        help="Maximum number of timestep points to show",
    )

    parser.add_argument(
        "--x-axis",
        choices=["steps", "tokens"],
        default="steps",
        help="X-axis type: 'steps' for training steps or 'tokens' for token count",
    )

    parser.add_argument(
        "--show-rank-labels",
        action="store_true",
        help="Show Start/Final rank labels on the right side of the plot",
    )

    parser.add_argument(
        "--title",
        type=str,
        help="Custom title for the plot (overrides default title)",
    )

    parser.add_argument(
        "--xlim-min",
        type=float,
        help="Minimum x-axis limit (for token mode, specify in token count)",
    )

    parser.add_argument(
        "--xlim-max",
        type=float,
        help="Maximum x-axis limit (for token mode, specify in token count)",
    )

    parser.add_argument(
        "--no-value-labels",
        action="store_true",
        help="Hide per-value labels (perplexity values) on data points",
    )

    return parser


def select_label_points(
    df: pd.DataFrame,
    x_col: str,
    max_points: int,
) -> set[float]:
    if max_points < MIN_POINTS_FOR_SAMPLING:
        raise ValueError(
            "max_points must be at least 2 to preserve first and last points"
        )

    # Only work with original (non-interpolated) data
    original_df = df[~df["is_interpolated"]].copy()

    selected_times = set()

    for combo in original_df["param_data_combo"].unique():
        combo_data = original_df[original_df["param_data_combo"] == combo].copy()
        combo_data = combo_data.sort_values(x_col)

        original_times = sorted(combo_data[x_col].unique())

        if len(original_times) <= max_points:
            # Use all original points if we have few enough
            selected_times.update(original_times)
        else:
            # Downsample original points only
            combo_selected = [original_times[0], original_times[-1]]  # Keep first/last

            if max_points > MIN_POINTS_FOR_SAMPLING:
                middle_points_needed = max_points - MIN_POINTS_FOR_SAMPLING
                middle_times = original_times[1:-1]  # Exclude first and last

                if middle_points_needed >= len(middle_times):
                    combo_selected.extend(middle_times)
                else:
                    # Sample evenly spaced middle points
                    indices = [
                        int(i * len(middle_times) / (middle_points_needed + 1))
                        for i in range(1, middle_points_needed + 1)
                    ]
                    selected_middle = [middle_times[i] for i in indices]
                    combo_selected.extend(selected_middle)

            selected_times.update(combo_selected)

    return selected_times


def prepare_interpolated_data(
    df: pd.DataFrame,
    params: list[str],
    data: list[str],
    x_axis: str,
    common_start_x: float | None = None,
) -> pd.DataFrame:
    x_col = "tokens" if x_axis == "tokens" else "step"

    print(
        f"Using linear interpolation to fill missing timestep data for "
        f"{len(params) * len(data)} param×data combinations"
    )

    # Find the min of min x-values across all combinations (earliest common point)
    min_x_per_combo = df.groupby("param_data_combo")[x_col].min()
    common_start_x = min_x_per_combo.min()
    x_label = "token" if x_axis == "tokens" else "step"
    print(
        f"Starting plot at {x_label} {common_start_x} "
        "(earliest common point across all combinations)"
    )

    # Get all unique x-values from the common start point
    all_x_values = sorted([x for x in df[x_col].unique() if x >= common_start_x])

    # Interpolate missing values for each combination
    interpolated_rows = []
    for combo in df["param_data_combo"].unique():
        combo_data = df[df["param_data_combo"] == combo].copy()
        combo_data = combo_data.sort_values(x_col)

        # Track which x-values had original data
        original_x_values = set(combo_data[x_col].values)

        # Interpolate values for ALL x-values from common start (not just within range)
        interpolated_data = combo_data.set_index(x_col).reindex(all_x_values)
        interpolated_data["value"] = interpolated_data["value"].interpolate(
            method="linear"
        )

        # Handle extrapolation for points before/after data range
        # Forward fill for points before first data point
        interpolated_data["value"] = interpolated_data["value"].bfill()
        # Backward fill for points after last data point
        interpolated_data["value"] = interpolated_data["value"].ffill()

        # Mark which values are interpolated vs original
        interpolated_data["is_interpolated"] = [
            x_val not in original_x_values for x_val in all_x_values
        ]

        # Forward fill params and data columns (they're constant for this combo)
        interpolated_data["params"] = combo_data["params"].iloc[0]
        interpolated_data["data"] = combo_data["data"].iloc[0]
        interpolated_data["param_data_combo"] = combo

        # Add other columns if they exist (e.g., tokens when x_col is
        # "step", or step when x_col is "tokens")
        if x_axis == "tokens" and "step" in combo_data.columns:
            # For token-based plots, we need to maintain the step-token relationship
            # This is complex because tokens might not map directly
            # to our interpolated points
            # For now, we'll set step to None for interpolated points
            step_mapping = dict(zip(combo_data[x_col], combo_data["step"]))
            interpolated_data["step"] = [
                step_mapping.get(x_val) for x_val in all_x_values
            ]
        elif x_axis == "steps" and "tokens" in combo_data.columns:
            # For step-based plots with token data, maintain step-token relationship
            token_mapping = dict(zip(combo_data[x_col], combo_data["tokens"]))
            interpolated_data["tokens"] = [
                token_mapping.get(x_val) for x_val in all_x_values
            ]

        # Reset index to get x_col back as column
        interpolated_data = interpolated_data.reset_index()
        interpolated_rows.append(interpolated_data)

    df_interpolated = pd.concat(interpolated_rows, ignore_index=True)

    # Remove rows where interpolation couldn't fill
    df_interpolated = df_interpolated.dropna(subset=["value"])

    print(f"After interpolation: {df_interpolated.shape[0]} data points")
    return df_interpolated


def resolve_data_groups(data_args: list[str]) -> list[str]:
    named_groups = {
        "base": BASE_RECIPES,
        "base_qc": BASE_AND_QC,
        "no_ablations": RECIPES_WITHOUT_ABLATIONS,
        **CUSTOM_RECIPE_FAMILIES,
        **{
            f"{k.replace('_performance', '')}": v
            for k, v in PPL_PERFORMANCE_RECIPE_CHUNKS.items()
        },
        **{
            f"{k.replace('_performance', '')}": v
            for k, v in OLMES_PERFORMANCE_RECIPE_CHUNKS.items()
        },
    }

    resolved_recipes = []
    for arg in data_args:
        if arg in named_groups:
            resolved_recipes.extend(named_groups[arg])
        elif arg == "all":
            return data_args
        else:
            resolved_recipes.append(arg)

    return list(dict.fromkeys(resolved_recipes))


def apply_first_last_filter(
    bump_data: pd.DataFrame, time_col: str = "time", category_col: str = "category"
) -> pd.DataFrame:
    """Extract only first and last time points for each category (compressed bump view).

    This creates a compressed visualization showing only the initial and final
    rankings for each category, connected by straight lines. Useful for
    highlighting ranking changes without trajectory noise.
    """
    filtered_data = []
    for category in bump_data[category_col].unique():
        cat_data = bump_data[bump_data[category_col] == category].copy()
        time_values = sorted(cat_data[time_col].unique())

        # Get first and last time points
        first_time = time_values[0]
        last_time = time_values[-1]

        # Add first and last rows for this category
        first_row = cat_data[cat_data[time_col] == first_time]
        last_row = cat_data[cat_data[time_col] == last_time]

        filtered_data.extend([first_row, last_row])

    return pd.concat(filtered_data, ignore_index=True)


# TODO: Refactor this function - it's overly complex (131 statements, 24 branches)
# Consider breaking into smaller functions for data preparation, plotting, and output
def plot_bump_timesteps(  # noqa: C901, PLR0912, PLR0915
    metric: str = "pile-valppl",
    params: list[str] | None = None,
    data: list[str] | None = None,
    exclude_data: list[str] | None = None,
    save_path: str | None = None,
    show_plot: bool = True,
    figsize: tuple[float, float] = (14, 8),
    min_step: float | None = None,
    max_step: float | None = None,
    first_last_only: bool = False,
    interpolate: bool = False,
    max_points: int | None = None,
    width_per_point: float = 0.8,
    height_per_line: float = 0.15,
    x_axis: str = "steps",
    show_rank_labels: bool = False,
    custom_title: str | None = None,
    xlim_min: float | None = None,
    xlim_max: float | None = None,
    show_value_labels: bool = True,
) -> None:
    dd = DataDecide()

    exclude_data = exclude_data or []

    # Handle "all" params like other scripts
    if params is None or (len(params) == 1 and params[0] == "all"):
        params = dd.select_params("all")

    # Resolve named data groups first, then handle "all" and exclusions
    if data is None:
        data = ["all"]

    resolved_data = resolve_data_groups(data)
    if len(resolved_data) == 1 and resolved_data[0] == "all":
        data = dd.select_data("all", exclude=exclude_data)
    else:
        data = [d for d in resolved_data if d not in (exclude_data or [])]

    metrics = [metric]

    print(f"Preparing data for recipes: {data}")
    print(f"Model sizes: {params}")
    print(f"Metric: {metrics}")

    # Get training curve data (not aggregated to preserve timestep dimension)
    df = dd.prepare_plot_data(
        params=params,
        data=data,
        metrics=metrics,
        aggregate_seeds=True,
        auto_filter=True,
        melt=True,
    )

    # Add token information if x_axis is "tokens"
    if x_axis == "tokens":
        token_info = dd.full_eval[
            ["params", "data", "step", "tokens"]
        ].drop_duplicates()
        df = df.merge(token_info, on=["params", "data", "step"], how="left")
        print(
            f"Added token information. Token range: {df['tokens'].min():.0f} to "
            f"{df['tokens'].max():.0f}"
        )

    print(f"\nData after prepare_plot_data: {df.shape}")
    print(f"Unique params in df: {sorted(df['params'].unique())}")
    print(f"Unique data in df: {sorted(df['data'].unique())}")
    if x_axis == "steps":
        print(f"Step range: {df['step'].min()} to {df['step'].max()}")
    else:
        print(f"Token range: {df['tokens'].min():.0f} to {df['tokens'].max():.0f}")
        print(f"Step range: {df['step'].min()} to {df['step'].max()}")

    # Filter by step range if specified
    if min_step is not None:
        df = df[df["step"] >= min_step]
        print(f"After min_step filter: {df.shape}")

    if max_step is not None:
        df = df[df["step"] <= max_step]
        print(f"After max_step filter: {df.shape}")

    if df.empty:
        print(f"No data found for model sizes {params} with the specified filters")
        return

    # Create param x data combinations as categories for bump plot
    df["param_data_combo"] = df["params"].astype(str) + "-" + df["data"].astype(str)

    # Mark all initial data as original (not interpolated)
    df["is_interpolated"] = False

    # Initialize common_start_x for potential use in interpolation
    common_start_x = None

    if interpolate:
        df = prepare_interpolated_data(df, params, data, x_axis, common_start_x)
    else:
        # Mark all values as original (not interpolated)
        df["is_interpolated"] = False

        # Show data coverage info
        total_possible_combos = len(params) * len(data)
        available_combos = df["param_data_combo"].nunique()

        print(
            f"Data coverage: {available_combos} of {total_possible_combos} "
            "param×data combinations have data"
        )
        print("Using all available data without requiring complete coverage")

    # Find common start point across all trajectories (maximum of minimum start points)
    x_col = "tokens" if x_axis == "tokens" else "step"
    min_times_per_combo = df.groupby("param_data_combo")[x_col].min()
    common_start_time = min_times_per_combo.max()

    # Filter all trajectories to start from the common start point
    original_shape = df.shape[0]
    df = df[df[x_col] >= common_start_time].copy()
    filtered_shape = df.shape[0]

    x_label = "token" if x_axis == "tokens" else "step"
    print(f"Aligned all trajectories to common start {x_label}: {common_start_time}")
    print(f"Filtered from {original_shape} to {filtered_shape} points for alignment")

    # Generate label points selection if max_points is specified
    label_time_points = None
    if max_points is not None:
        print(
            f"\nSelecting max {max_points} label points per trajectory from "
            "original data"
        )
        x_col = "tokens" if x_axis == "tokens" else "step"
        label_time_points = select_label_points(df, x_col, max_points)
        print(f"Selected {len(label_time_points)} unique time points for labeling")

    # Create bump plot data using x-axis and param x data combinations as categories
    x_col = "tokens" if x_axis == "tokens" else "step"
    x_label = "token count" if x_axis == "tokens" else "training steps"

    bump_data = df.rename(
        columns={
            x_col: "time",  # X-axis values (steps or tokens) become time dimension
            "param_data_combo": "category",  # Param x Data combinations become
            # categories (trajectories)
            "value": "score",  # Performance values (lower is better for perplexity)
        }
    )[["time", "category", "score", "is_interpolated"]]

    # Keep original perplexity values for labeling (before inversion)
    bump_data["original_ppl"] = bump_data["score"].copy()

    # Invert scores for ranking (higher score = better rank)
    bump_data["score"] = -bump_data["score"]
    metric_str = metric.replace("_", " ").replace("-", " ").title()

    print("\nBump plot data preview:")
    print(bump_data.head(10))
    print(f"\nBump data shape: {bump_data.shape}")
    print(f"Categories (recipes): {sorted(bump_data['category'].unique())}")
    print(f"Time points: {len(sorted(bump_data['time'].unique()))} unique points")

    # DEBUG: Check rankings at first and last time points
    time_points = sorted(bump_data["time"].unique())
    first_time = time_points[0]
    last_time = time_points[-1]

    print("\n=== DEBUG: Timestep Bump Plot ===")
    print(f"First step: {first_time}")
    print(f"Last step: {last_time}")

    first_data = bump_data[bump_data["time"] == first_time].copy()
    first_data = first_data.sort_values("score", ascending=False)
    first_data["rank"] = range(1, len(first_data) + 1)
    print("\nFirst step rankings (LEFT labels):")
    for _, row in first_data.iterrows():
        print(
            f"  Rank {row['rank']}: {row['category']} (ppl={row['original_ppl']:.2f})"
        )

    last_data = bump_data[bump_data["time"] == last_time].copy()
    last_data = last_data.sort_values("score", ascending=False)
    last_data["rank"] = range(1, len(last_data) + 1)
    print("\nLast step rankings (RIGHT labels):")
    for _, row in last_data.iterrows():
        print(
            f"  Rank {row['rank']}: {row['category']} (ppl={row['original_ppl']:.2f})"
        )

    print("\n=== End Debug ===\n")

    # Apply first-last filter if requested
    if first_last_only:
        bump_data = apply_first_last_filter(
            bump_data, time_col="time", category_col="category"
        )
        print(f"Applied first-last-only filter: {len(bump_data)} data points remaining")

    # Create custom theme with extended colors for better distinction
    num_categories = len(bump_data["category"].unique())
    custom_theme = create_bump_theme_with_colors(num_categories)
    print(f"Using extended color palette for {num_categories} categories")

    # Dynamic figure sizing based on data complexity
    num_time_points = len(bump_data["time"].unique())

    # Pure scaling: width = time_points * scaling_factor,
    # height = categories * scaling_factor
    dynamic_width = num_time_points * width_per_point
    dynamic_height = num_categories * height_per_line

    dynamic_figsize = (dynamic_width, dynamic_height)
    print(
        f"Dynamic figure size: {dynamic_figsize[0]:.1f} x {dynamic_figsize[1]:.1f} "
        f"({num_time_points} points, {num_categories} lines)"
    )

    with FigureManager(
        PlotConfig(
            layout={
                "rows": 1,
                "cols": 1,
                "figsize": dynamic_figsize,
                "xmargin": 0.15,
                "ymargin": 0.15 * (10 / num_categories),
            },
            style={"theme": custom_theme},
        )
    ) as fm:
        fm.plot(
            "bump",
            0,
            0,
            bump_data,
            time_col="time",
            value_col="score",
            category_col="category",
            marker="o",
            linewidth=2,
            title=custom_title
            if custom_title
            else f"Rankings Over {x_label.title()} ({metric_str})",
        )

        # Add annotations and labels
        ax = fm.get_axes(0, 0)
        add_left_ranking_labels(ax, bump_data)
        if show_value_labels:
            add_value_annotations(
                ax, bump_data, first_last_only, label_time_points, show_rank_labels
            )

        # Format x-axis to show labels nicely
        if x_axis == "tokens":
            # Set log scale for token counts with proper formatting
            ax.set_xscale("log")
            ax.set_xlabel("Token Count (log scale)")
            # Set x-limits for token mode
            if xlim_min is not None or xlim_max is not None:
                # Use custom limits if provided
                min_limit = xlim_min if xlim_min is not None else 2e8
                max_limit = xlim_max if xlim_max is not None else 1.2e11
                ax.set_xlim(min_limit, max_limit)
            else:
                # Default limits (0.5B to 120B)
                ax.set_xlim(2e8, 1.2e11)
            # Use FuncFormatter to properly format log scale tick labels
            ax.xaxis.set_major_formatter(
                ticker.FuncFormatter(lambda x, _: format_token_count(x))
            )
        else:
            # For steps, manually set ticks and format them
            x_values = sorted(bump_data["time"].unique())
            ax.set_xticks(x_values[:: max(1, len(x_values) // 8)])  # Show ~8 labels max
            ax.set_xticklabels([format_step_label(s) for s in ax.get_xticks()])
            ax.set_xlabel("Training Step")

        # Add metric label and interpolation legend if needed
        # metric_label = metric_str + " Values"
        # if interpolate and bump_data["is_interpolated"].any():
        #     metric_label += "\n(unlabeled points interpolated)"

        # ax.text(
        #     0.02,
        #     1.5,
        #     metric_label,
        #     transform=ax.transData,
        #     fontsize=8,
        #     ha="left",
        #     va="center",
        #     bbox={
        #         "boxstyle": "round,pad=0.2",
        #         "facecolor": "white",
        #         "alpha": 0.8,
        #         "edgecolor": "gray",
        #     },
        # )  # Commented out - metric label annotation was placed too far to the side

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Plot saved to: {save_path}")

    if show_plot:
        plt.show()

    if not show_plot and not save_path:
        print("Warning: Plot not saved or displayed. Use --save or remove --no-show")


def main() -> None:
    parser = create_arg_parser()
    args = parser.parse_args()

    show_plot = not args.no_show
    figsize = tuple(args.figsize)

    plot_bump_timesteps(
        metric=args.metric,
        params=args.params,
        data=args.data,
        exclude_data=args.exclude_data,
        save_path=args.save,
        show_plot=show_plot,
        figsize=figsize,
        min_step=args.min_step,
        max_step=args.max_step,
        first_last_only=getattr(args, "first_last_only", False),
        interpolate=getattr(args, "interpolate", False),
        max_points=getattr(args, "max_points", None),
        width_per_point=getattr(args, "width_per_point", 0.8),
        height_per_line=getattr(args, "height_per_line", 0.15),
        x_axis=getattr(args, "x_axis", "steps"),
        show_rank_labels=getattr(args, "show_rank_labels", False),
        custom_title=getattr(args, "title", None),
        xlim_min=getattr(args, "xlim_min", None),
        xlim_max=getattr(args, "xlim_max", None),
        show_value_labels=not getattr(args, "no_value_labels", False),
    )


if __name__ == "__main__":
    main()
