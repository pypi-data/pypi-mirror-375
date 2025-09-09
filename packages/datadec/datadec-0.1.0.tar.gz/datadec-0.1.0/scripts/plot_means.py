#!/usr/bin/env python3

from __future__ import annotations

import argparse
from typing import Any

import matplotlib.pyplot as plt

from datadec import DataDecide
from dr_plotter import FigureManager
from dr_plotter.configs import PlotConfig, PositioningConfig


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot mean training curves with faceted layout for DataDecide eval"
    )

    # Faceting structure (mutually exclusive)
    facet_group = parser.add_mutually_exclusive_group(required=True)
    facet_group.add_argument(
        "--row",
        choices=["params", "data", "metrics"],
        help="Dimension to use for row faceting",
    )
    facet_group.add_argument(
        "--col",
        choices=["params", "data", "metrics"],
        help="Dimension to use for column faceting",
    )

    parser.add_argument(
        "--lines",
        choices=["params", "data", "metrics"],
        required=True,
        help="Dimension to use for line grouping within each subplot",
    )

    # Value selection
    parser.add_argument(
        "--row_values",
        nargs="+",
        help="Values for row dimension (or 'all' for all available)",
    )
    parser.add_argument(
        "--col_values",
        nargs="+",
        help="Values for column dimension (or 'all' for all available)",
    )
    parser.add_argument(
        "--line_values",
        nargs="+",
        required=True,
        help="Values for line dimension (or 'all' for all available)",
    )

    # Fixed dimension (for dimensions not used in plotting)
    parser.add_argument(
        "--fixed",
        choices=["params", "data", "metrics"],
        help="Dimension to hold constant (not used in row/col/lines)",
    )
    parser.add_argument(
        "--fixed-values",
        nargs="+",
        help="Values for the fixed dimension",
    )

    # Data filtering (derived from dimensional arguments)
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

    # Legend (reused from plot_seeds)
    parser.add_argument(
        "--legend",
        choices=["subplot", "grouped", "figure"],
        default="subplot",
        help="Legend strategy: subplot (per-axes), grouped (by-channel), figure",
    )

    # Output (reused from plot_seeds)
    parser.add_argument("--save", type=str, help="Save plot to file (specify path)")
    parser.add_argument(
        "--no-show", action="store_true", help="Don't display plot interactively"
    )

    # Layout (reused from plot_seeds)
    parser.add_argument(
        "--figsize-per-subplot",
        type=float,
        default=4.0,
        help="Figure size per subplot (default: 4.0)",
    )
    parser.add_argument(
        "--no-sharex",
        action="store_true",
        help="Disable x-axis sharing across subplots",
    )
    parser.add_argument(
        "--no-sharey",
        action="store_true",
        help="Disable y-axis sharing across subplots",
    )

    # Axis configuration (reused from plot_seeds)
    parser.add_argument(
        "--xlog", action="store_true", help="Use logarithmic scale for x-axis"
    )
    parser.add_argument(
        "--ylog", action="store_true", help="Use logarithmic scale for y-axis"
    )

    # Axis limits (new)
    parser.add_argument(
        "--xlim",
        nargs=2,
        type=float,
        metavar=("MIN", "MAX"),
        help="X-axis limits (e.g., --xlim 0 1000)",
    )
    parser.add_argument(
        "--ylim",
        nargs=2,
        type=float,
        metavar=("MIN", "MAX"),
        help="Y-axis limits (e.g., --ylim 2.5 4.0)",
    )

    return parser


def resolve_dimension_values(
    dimension: str,
    values: list[str] | None,
    dd: Any,
    params: list[str],
    data: list[str],
    metrics: list[str],
) -> list[str]:
    if dimension == "params":
        if values is None or (len(values) == 1 and values[0] == "all"):
            return params
        return values
    elif dimension == "data":
        if values is None or (len(values) == 1 and values[0] == "all"):
            return data
        return values
    elif dimension == "metrics":
        if values is None or (len(values) == 1 and values[0] == "all"):
            return metrics
        return values
    else:
        raise ValueError(f"Unknown dimension: {dimension}")


# TODO: Refactor this function - it's overly complex (86 statements, 28 branches)
# Consider breaking into smaller functions for data preparation, plotting, and format
def plot_means(  # noqa: C901, PLR0912, PLR0915
    row: str | None = None,
    col: str | None = None,
    lines: str | None = None,
    row_values: list[str] | None = None,
    col_values: list[str] | None = None,
    line_values: list[str] | None = None,
    fixed: str | None = None,
    fixed_values: list[str] | None = None,
    exclude_params: list[str] | None = None,
    exclude_data: list[str] | None = None,
    legend_strategy: str = "subplot",
    save_path: str | None = None,
    show_plot: bool = True,
    figsize_per_subplot: float = 4.0,
    sharex: bool = True,
    sharey: bool = True,
    xlog: bool = False,
    ylog: bool = False,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
) -> None:
    dd = DataDecide()

    exclude_params = exclude_params or []
    exclude_data = exclude_data or []

    # Map dimension names to DataFrame column names
    dim_to_col = {"params": "params", "data": "data", "metrics": "metric"}

    # Determine which dimensions we need and collect all required values
    facet_dim = row if row else col
    dimensions_used = {facet_dim, lines}
    if fixed:
        dimensions_used.add(fixed)

    # Collect all values needed for each dimension
    all_params = []
    all_data = []
    all_metrics = []

    # Handle explicit dimension assignments
    for dim in ["params", "data", "metrics"]:
        if dim == facet_dim:
            values = row_values if row else col_values
        elif dim == lines:
            values = line_values
        elif dim == fixed:
            values = fixed_values
        else:
            values = None

        if dim == "params":
            if values:
                all_params = resolve_dimension_values("params", values, dd, [], [], [])
        elif dim == "data":
            if values:
                all_data = resolve_dimension_values("data", values, dd, [], [], [])
        elif dim == "metrics" and values:
            all_metrics = resolve_dimension_values("metrics", values, dd, [], [], [])

    # Use "all" for dimensions not explicitly specified
    if not all_params:
        all_params = dd.select_params("all", exclude=exclude_params)
    if not all_data:
        all_data = dd.select_data("all", exclude=exclude_data)
    if not all_metrics:
        all_metrics = ["pile-valppl"]  # default metric

    # Resolve final dimension values for plotting
    facet_values = resolve_dimension_values(
        facet_dim,
        row_values if row else col_values,
        dd,
        all_params,
        all_data,
        all_metrics,
    )
    line_values_resolved = resolve_dimension_values(
        lines, line_values, dd, all_params, all_data, all_metrics
    )

    # Debug what we're passing to prepare_plot_data
    print(f"Params passed to prepare_plot_data: {all_params}")
    print(f"Data passed to prepare_plot_data: {all_data}")
    print(f"Metrics passed to prepare_plot_data: {all_metrics}")

    # Prepare data with all requested metrics (aggregate seeds for mean plotting)
    df = dd.prepare_plot_data(
        params=all_params,
        data=all_data,
        metrics=all_metrics,
        aggregate_seeds=True,
        auto_filter=True,
        melt=True,
    )
    print(f"Data after prepare_plot_data: {df.shape}")
    print(f"Unique params in df: {sorted(df['params'].unique())}")
    print(f"Unique data in df: {sorted(df['data'].unique())}")
    print(f"Unique metrics in df: {sorted(df['metric'].unique())}")

    # Data is already aggregated by prepare_plot_data, just use it directly
    print(f"Facet dimension: {facet_dim}, values: {facet_values}")
    print(f"Line dimension: {lines}, values: {line_values_resolved}")
    print(f"Unique facet values in data: {sorted(df[dim_to_col[facet_dim]].unique())}")
    print(f"Unique line values in data: {sorted(df[dim_to_col[lines]].unique())}")

    # Calculate dimensions
    nfacets = len(facet_values)
    if row:
        nrows, ncols = nfacets, 1
        figsize = (figsize_per_subplot * ncols, figsize_per_subplot * nrows)
    else:
        nrows, ncols = 1, nfacets
        figsize = (figsize_per_subplot * ncols, figsize_per_subplot * nrows)

    # Layout configuration
    if legend_strategy == "figure":
        tight_layout_rect = (0.01, 0.15, 0.99, 0.97)
        positioning_config = PositioningConfig(legend_y_offset_factor=0.02)
        legend_config = {
            "strategy": legend_strategy,
            "position": "lower center",
            "channel_titles": {lines: lines.title()},
            "positioning_config": positioning_config,
        }
    else:
        tight_layout_rect = (0.01, 0.01, 0.99, 0.97)
        legend_config = {
            "strategy": legend_strategy,
            "position": "best",
            "channel_titles": {lines: lines.title()},
        }

    # Create title with fixed dimension info
    fixed_str = ", ".join(fixed_values)
    title_parts = [
        f"({fixed.title()}: {fixed_str})",
        f"{facet_dim.title()} x {lines.title()}",
    ]

    layout_config = {
        "rows": nrows,
        "cols": ncols,
        "figsize": figsize,
        "tight_layout_pad": 0.5,
        "tight_layout_rect": tight_layout_rect,
        "subplot_kwargs": {"sharex": sharex, "sharey": sharey},
        "figure_title": f"{' '.join(title_parts)}",
    }

    if xlog:
        layout_config["xscale"] = "log"
    if ylog:
        layout_config["yscale"] = "log"

    with FigureManager(
        PlotConfig(
            layout=layout_config,
            legend=legend_config,
            kwargs={"suptitle_y": 0.98},
        )
    ) as fm:
        fm.plot_faceted(
            data=df,
            plot_type="line",
            rows=dim_to_col[facet_dim] if row else None,
            cols=dim_to_col[facet_dim] if col else None,
            lines=dim_to_col[lines],
            x="step",
            y="value",
            linewidth=1.5,
            alpha=0.8,
            marker=None,
            row_order=facet_values if row else None,
            col_order=facet_values if col else None,
            lines_order=line_values_resolved,
            row_titles=bool(row),
            col_titles=bool(col),
            exterior_x_label="Training Steps",
        )

        # Apply axis limits if specified
        if xlim or ylim:
            for facet_idx in range(nfacets):
                ax = fm.get_axes(facet_idx, 0) if row else fm.get_axes(0, facet_idx)
                if xlim:
                    ax.set_xlim(xlim)
                if ylim:
                    ax.set_ylim(ylim)

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
    sharex = not args.no_sharex
    sharey = not args.no_sharey
    xlim = tuple(args.xlim) if args.xlim else None
    ylim = tuple(args.ylim) if args.ylim else None

    plot_means(
        row=args.row,
        col=args.col,
        lines=args.lines,
        row_values=args.row_values,
        col_values=args.col_values,
        line_values=args.line_values,
        fixed=args.fixed,
        fixed_values=getattr(args, "fixed_values", None),
        exclude_params=args.exclude_params,
        exclude_data=args.exclude_data,
        legend_strategy=args.legend,
        save_path=args.save,
        show_plot=show_plot,
        figsize_per_subplot=args.figsize_per_subplot,
        sharex=sharex,
        sharey=sharey,
        xlog=args.xlog,
        ylog=args.ylog,
        xlim=xlim,
        ylim=ylim,
    )


if __name__ == "__main__":
    main()
