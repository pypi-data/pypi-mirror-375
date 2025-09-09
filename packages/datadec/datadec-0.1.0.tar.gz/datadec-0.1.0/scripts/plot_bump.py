#!/usr/bin/env python3

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import pandas as pd

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


def format_perplexity(ppl_value: float) -> str:
    return f"{ppl_value:.2f}"


def create_extended_color_palette() -> list[str]:
    """Create a larger, more distinct color palette for many data recipes."""
    # Extended palette with 20+ distinct colors
    return [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",  # Original matplotlib
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
        "#aec7e8",
        "#ffbb78",
        "#98df8a",
        "#ff9896",
        "#c5b0d5",  # Lighter variants
        "#c49c94",
        "#f7b6d3",
        "#c7c7c7",
        "#dbdb8d",
        "#9edae5",
        "#393b79",
        "#637939",
        "#8c6d31",
        "#843c39",
        "#7b4173",  # Darker variants
        "#5254a3",
        "#8ca252",
        "#bd9e39",
        "#ad494a",
        "#a55194",
        "#6b6ecf",
        "#b5cf6b",
        "#e7ba52",
        "#d6616b",
        "#ce6dbd",  # Medium variants
        "#de9ed6",
        "#31a354",
        "#756bb1",
        "#636363",
        "#969696",  # Additional
    ]


def create_bump_theme_with_colors(num_categories: int) -> Theme:
    """Create a custom theme with extended color palette for bump plots."""
    import itertools

    from dr_plotter import consts

    extended_colors = create_extended_color_palette()

    # Use enough colors for the categories we have
    colors_to_use = extended_colors[: max(num_categories, len(extended_colors))]

    return Theme(
        name="bump_extended",
        parent=BUMP_PLOT_THEME,
        **{
            consts.get_cycle_key("hue"): itertools.cycle(colors_to_use),
        },
    )


def numerical_sort_key(param_size: str) -> float:
    """Convert parameter size string to numerical value for proper sorting."""
    if param_size.endswith("M"):
        return float(param_size[:-1])
    elif param_size.endswith("B"):
        return float(param_size[:-1]) * 1000
    else:
        return float(param_size)


def add_left_ranking_labels(ax: plt.Axes, bump_data: pd.DataFrame) -> None:
    """Add recipe name labels on the left side showing initial rankings."""

    # Get first time point data for initial rankings
    # (sort numerically, not alphabetically)
    time_points = sorted(bump_data["time"].unique(), key=numerical_sort_key)
    first_time = time_points[0]
    first_time_data = bump_data[bump_data["time"] == first_time].copy()
    first_time_data = first_time_data.sort_values("score", ascending=False)
    first_time_data["rank"] = range(1, len(first_time_data) + 1)

    # Add labels on the left side
    for _, row in first_time_data.iterrows():
        category_name = row["category"]
        rank = row["rank"]

        ax.text(
            -0.15,
            rank,  # Position to the left of the y-axis
            f"{rank}. {category_name}",
            transform=ax.transData,
            fontsize=9,
            ha="right",
            va="center",
            fontweight="bold",
            bbox={
                "boxstyle": "round,pad=0.3",
                "facecolor": "lightblue",
                "alpha": 0.7,
                "edgecolor": "navy",
            },
        )


def add_right_ranking_labels(ax: plt.Axes, bump_data: pd.DataFrame) -> None:
    time_points = sorted(bump_data["time"].unique(), key=numerical_sort_key)
    last_time = time_points[-1]
    last_time_data = bump_data[bump_data["time"] == last_time].copy()
    last_time_data = last_time_data.sort_values("score", ascending=False)
    last_time_data["rank"] = range(1, len(last_time_data) + 1)

    for _, row in last_time_data.iterrows():
        category_name = row["category"]
        rank = row["rank"]

        ax.text(
            len(time_points) - 1 + 0.15,
            rank,
            f"{rank}. {category_name}",
            transform=ax.transData,
            fontsize=9,
            ha="left",
            va="center",
            fontweight="bold",
            bbox={
                "boxstyle": "round,pad=0.3",
                "facecolor": "lightgreen",
                "alpha": 0.7,
                "edgecolor": "darkgreen",
            },
        )


def add_value_annotations(ax: plt.Axes, bump_data: pd.DataFrame) -> None:
    # Create mapping from model size names to numeric positions for x-axis
    # (sorted numerically)
    time_points = sorted(bump_data["time"].unique(), key=numerical_sort_key)
    time_to_x = {time_point: idx for idx, time_point in enumerate(time_points)}

    # Get the ranking data that BumpPlotter created (inverted y-axis, rank 1 at top)
    ranked_data = []
    for time_point in time_points:
        time_data = bump_data[bump_data["time"] == time_point].copy()
        time_data = time_data.sort_values("score", ascending=False)
        time_data["rank"] = range(1, len(time_data) + 1)
        ranked_data.append(time_data)

    all_ranked_data = pd.concat(ranked_data, ignore_index=True)

    # Add annotations for each point
    for _, row in all_ranked_data.iterrows():
        x_pos = time_to_x[row["time"]]
        y_pos = row["rank"]  # Rank position (1 = top)
        ppl_text = format_perplexity(row["original_ppl"])

        # Position text slightly above and to the right of each point
        ax.annotate(
            ppl_text,
            xy=(x_pos, y_pos),  # Point location
            xytext=(5, 8),  # Offset: 5 pixels right, 8 pixels up
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
            arrowprops=None,  # No arrow, just floating text
        )


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot bump chart rankings for datadecide"
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
        help="Param sizes (e.g., 150M 300M 1B) or 'all'",
    )

    parser.add_argument(
        "--data",
        nargs="+",
        default=["all"],
        help=(
            "Data recipes: 'all', 'base', 'base_qc', 'no_ablations', or names. "
            "Named groups: 'core_datasets', 'dolma17_variants', 'dclm_variants', "
            "'falcon_cc_variants', 'fineweb_variants', 'mix_with_baselines', "
            "'best_ppl', 'good_ppl', 'medium_ppl', 'poor_ppl', 'best_olmes', "
            "'good_olmes', 'medium_olmes', 'poor_olmes'"
        ),
    )

    parser.add_argument(
        "--exclude-params",
        nargs="+",
        default=[],
        help="Model parameter sizes to exclude when using 'all'",
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
        default=[12, 8],
        help="Figure size width height (default: 12 8)",
    )

    parser.add_argument(
        "--first-last-only",
        action="store_true",
        help="Show only first and last rankings (compressed view)",
    )

    return parser


def resolve_data_groups(data_args: list[str]) -> list[str]:
    """Resolve named data groups to actual recipe lists."""

    # Define all named groups
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
            # Let the main function handle "all"
            return data_args
        else:
            # Assume it's a specific recipe name
            resolved_recipes.append(arg)

    # Remove duplicates while preserving order
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


# TODO: Refactor this function - it has grown too large (85 statements)
# Consider breaking into smaller functions for data preparation, plotting, and output
def plot_bump(  # noqa: PLR0915
    metric: str = "pile-valppl",
    params: list[str] | None = None,
    data: list[str] | None = None,
    exclude_params: list[str] | None = None,
    exclude_data: list[str] | None = None,
    save_path: str | None = None,
    show_plot: bool = True,
    figsize: tuple[float, float] = (12, 8),
    first_last_only: bool = False,
) -> None:
    dd = DataDecide()

    exclude_params = exclude_params or []
    exclude_data = exclude_data or []

    # Handle "all" values and exclusions for params
    if params is None or (len(params) == 1 and params[0] == "all"):
        params = dd.select_params("all", exclude=exclude_params)

    # Resolve named data groups first, then handle "all" and exclusions
    if data is None:
        data = ["all"]

    resolved_data = resolve_data_groups(data)
    if len(resolved_data) == 1 and resolved_data[0] == "all":
        data = dd.select_data("all", exclude=exclude_data)
    else:
        # Filter out excluded data from resolved groups
        data = [d for d in resolved_data if d not in (exclude_data or [])]

    metrics = [metric]

    print(f"Preparing data for recipes: {data}")
    print(f"Model sizes: {params}")
    print(f"Metric: {metrics}")

    # Get training curve data (not aggregated for bump plot temporal dimension)
    df = dd.prepare_plot_data(
        params=params,
        data=data,
        metrics=metrics,
        aggregate_seeds=True,
        auto_filter=True,
        melt=True,
    )

    print(f"\nData after prepare_plot_data: {df.shape}")
    print(f"Unique params in df: {sorted(df['params'].unique())}")
    print(f"Unique data in df: {sorted(df['data'].unique())}")
    print(f"Step range: {df['step'].min()} to {df['step'].max()}")

    # Debug: Check what's happening with the final step filtering
    print("\nDebugging final step selection:")
    print(f"Max step globally: {df['step'].max()}")
    print("Step distribution by params:")
    step_by_params = df.groupby("params")["step"].agg(["min", "max", "count"])
    print(step_by_params)

    # The issue: different model sizes have different max steps!
    # We need to use the final available step for each model size
    final_step_per_params = df.groupby("params")["step"].max().reset_index()
    print("\nFinal step per model size:")
    print(final_step_per_params)

    # Get final performance for each (params, data) combination
    final_rows = []
    for params_size in df["params"].unique():
        params_df = df[df["params"] == params_size]
        max_step_for_params = params_df["step"].max()
        final_step_data = params_df[params_df["step"] == max_step_for_params]
        final_rows.append(final_step_data)

    final_step_df = pd.concat(final_rows, ignore_index=True)
    print(f"\nFinal step df shape: {final_step_df.shape}")
    print(f"Params in final step df: {sorted(final_step_df['params'].unique())}")

    # Create bump plot data while preserving original values for labels
    bump_data = final_step_df.rename(
        columns={
            "params": "time",  # Model sizes become time dimension
            "data": "category",  # Recipes become categories (trajectories)
            "value": "score",  # Performance values (lower is better for perplexity)
        }
    )[["time", "category", "score"]]

    # Keep original perplexity values for labeling (before inversion)
    bump_data["original_ppl"] = bump_data["score"].copy()

    bump_data["score"] = -bump_data["score"]
    metric_str = metric.replace("_", " ").replace("-", " ").title()

    print("\nBump plot data preview:")
    print(bump_data.head(10))
    print(f"\nBump data shape: {bump_data.shape}")
    print(f"Categories (recipes): {sorted(bump_data['category'].unique())}")
    print(f"Time points (model sizes): {sorted(bump_data['time'].unique())}")

    # DEBUG: Check rankings at first and last time points (sorted numerically)
    time_points = sorted(bump_data["time"].unique(), key=numerical_sort_key)
    first_time = time_points[0]
    last_time = time_points[-1]

    print("\n=== DEBUG: Label Alignment Issue ===")
    print(f"First time point: {first_time}")
    print(f"Last time point: {last_time}")

    # First time rankings (what left labels show)
    first_data = bump_data[bump_data["time"] == first_time].copy()
    first_data = first_data.sort_values("score", ascending=False)
    first_data["rank"] = range(1, len(first_data) + 1)
    print("\nFirst time rankings (LEFT labels):")
    for _, row in first_data.iterrows():
        print(
            f"  Rank {row['rank']}: {row['category']} "
            f"(ppl={row['original_ppl']:.2f}, score={row['score']:.2f})"
        )

    # Last time rankings (what right labels should show)
    last_data = bump_data[bump_data["time"] == last_time].copy()
    last_data = last_data.sort_values("score", ascending=False)
    last_data["rank"] = range(1, len(last_data) + 1)
    print("\nLast time rankings (RIGHT labels):")
    for _, row in last_data.iterrows():
        print(
            f"  Rank {row['rank']}: {row['category']} "
            f"(ppl={row['original_ppl']:.2f}, score={row['score']:.2f})"
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

    with FigureManager(
        PlotConfig(
            layout={
                "rows": 1,
                "cols": 1,
                "figsize": figsize,
                "ymargin": 0.0,
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
            title=f"Recipe Rank by Model Size ({metric_str})",
        )

        # Add annotations and labels
        ax = fm.get_axes(0, 0)
        add_left_ranking_labels(ax, bump_data)
        add_right_ranking_labels(ax, bump_data)
        add_value_annotations(ax, bump_data)

        # Add annotation style label positioned below the highest ranking line (rank 1)
        # Position it at y=1.5 (between rank 1 and rank 2) to avoid collision
        metric_label = metric_str + " Values"
        ax.text(
            0.02,
            1.5,
            metric_label,
            fontsize=8,
            ha="left",
            va="center",
            bbox={
                "boxstyle": "round,pad=0.2",
                "facecolor": "white",
                "alpha": 0.8,
                "edgecolor": "gray",
            },
        )

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

    plot_bump(
        metric=args.metric,
        params=args.params,
        data=args.data,  # Will be resolved inside plot_bump function
        exclude_params=args.exclude_params,
        exclude_data=args.exclude_data,
        save_path=args.save,
        show_plot=show_plot,
        figsize=figsize,
        first_last_only=getattr(args, "first_last_only", False),
    )


if __name__ == "__main__":
    main()
