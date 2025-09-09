#!/usr/bin/env python3
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt

from datadec import DataDecide
from dr_plotter import FigureManager
from dr_plotter.configs import PlotConfig, PositioningConfig


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot training curves with multiple seeds for DataDecide evaluation"
    )

    parser.add_argument(
        "metric", help="Metric to plot (e.g., pile-valppl, mmlu_average_acc_raw)"
    )

    parser.add_argument(
        "--params",
        nargs="+",
        default=["all"],
        help="Model parameter sizes to include (e.g., 10M 60M 90M) or 'all'",
    )

    parser.add_argument(
        "--data",
        nargs="+",
        default=["all"],
        help="Data recipes to include (e.g., C4 Dolma1.7) or 'all' for all available",
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

    parser.add_argument(
        "--legend",
        choices=["subplot", "grouped", "figure"],
        default="subplot",
        help="Legend strategy: subplot (per-axes), grouped (by-channel), figure",
    )

    parser.add_argument("--save", type=str, help="Save plot to file (specify path)")

    parser.add_argument(
        "--no-show", action="store_true", help="Don't display plot interactively"
    )

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

    parser.add_argument(
        "--xlog", action="store_true", help="Use logarithmic scale for x-axis"
    )

    parser.add_argument(
        "--ylog", action="store_true", help="Use logarithmic scale for y-axis"
    )

    return parser


def plot_seeds(
    metric: str,
    params: list[str] | None = None,
    data: list[str] | None = None,
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
) -> None:
    dd = DataDecide()

    exclude_params = exclude_params or []
    exclude_data = exclude_data or []

    # Handle "all" values and exclusions
    if params is None or (len(params) == 1 and params[0] == "all"):
        params = dd.select_params("all", exclude=exclude_params)
    if data is None or (len(data) == 1 and data[0] == "all"):
        data = dd.select_data("all", exclude=exclude_data)

    df = dd.prepare_plot_data(
        params=params, data=data, metrics=[metric], auto_filter=True, melt=True
    )

    metric_label = metric.replace("_", " ").title()
    nparams = len(params)
    ndata = len(data)

    # Adjust layout based on legend strategy
    if legend_strategy == "figure":
        tight_layout_rect = (0.01, 0.1, 0.99, 0.97)  # Leave less space at bottom
        # Custom positioning config to move legend closer to bottom
        positioning_config = PositioningConfig(legend_y_offset_factor=0.02)
        legend_config = {
            "strategy": legend_strategy,
            "position": "lower center",
            "channel_titles": {"seed": "Seed"},
            "positioning_config": positioning_config,
        }
    else:
        tight_layout_rect = (0.01, 0.01, 0.99, 0.97)  # Standard spacing
        legend_config = {
            "strategy": legend_strategy,
            "position": "best",
            "channel_titles": {"seed": "Seed"},
        }

    layout_config = {
        "rows": nparams,
        "cols": ndata,
        "figsize": (figsize_per_subplot * ndata, figsize_per_subplot * nparams),
        "tight_layout_pad": 0.5,
        "tight_layout_rect": tight_layout_rect,
        "subplot_kwargs": {"sharex": sharex, "sharey": sharey},
        "figure_title": f"{metric_label}: All Seeds, Model Size x Data Recipe",
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
            rows="params",
            cols="data",
            lines="seed",
            x="step",
            y="value",
            linewidth=1.2,
            alpha=0.7,
            marker=None,
            row_order=params,
            col_order=data,
            row_titles=True,
            col_titles=True,
            exterior_x_label="Training Steps",
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
    sharex = not args.no_sharex
    sharey = not args.no_sharey

    plot_seeds(
        metric=args.metric,
        params=args.params,
        data=args.data,
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
    )


if __name__ == "__main__":
    main()
