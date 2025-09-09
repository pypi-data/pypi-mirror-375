#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

import matplotlib.pyplot as plt
import pandas as pd

from datadec import DataDecide
from dr_plotter import FigureManager
from dr_plotter.configs import FacetingConfig, LegendConfig, PlotConfig


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified DataDecide plotting example using the streamlined API"
    )

    # Plot configuration options
    parser.add_argument(
        "--metrics",
        nargs="+",
        default=["pile-valppl", "mmlu_average_acc_raw"],
        help="Metrics to plot (e.g., pile-valppl, mmlu_average_acc_raw)",
    )
    parser.add_argument(
        "--recipes",
        nargs="+",
        default=["C4", "Dolma1.7", "DCLM-Baseline"],
        help="Data recipes to include (in order for subplot columns)",
    )
    parser.add_argument(
        "--model-sizes",
        nargs="+",
        default=["150M", "1B"],
        help="Model sizes to include (in order for line styling)",
    )

    # Display options
    parser.add_argument(
        "--x-log", action="store_true", help="Use log scale for X-axis (training steps)"
    )
    parser.add_argument(
        "--y-log", action="store_true", help="Use log scale for Y-axis (metric values)"
    )
    parser.add_argument(
        "--aggregate-seeds",
        action="store_true",
        help="Aggregate results across seeds (show means only)",
    )
    parser.add_argument("--save-path", help="Save plot to file (specify path)")
    parser.add_argument(
        "--no-show", action="store_true", help="Don't display plot interactively"
    )

    # Axis limits
    parser.add_argument(
        "--xlim", nargs=2, type=float, metavar=("MIN", "MAX"), help="X-axis limits"
    )
    parser.add_argument(
        "--ylim", nargs=2, type=float, metavar=("MIN", "MAX"), help="Y-axis limits"
    )

    return parser


def create_faceted_plot(
    df: pd.DataFrame,
    metrics: list[str],
    recipes: list[str],
    model_sizes: list[str],
    x_log: bool = False,
    y_log: bool = False,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    save_path: str | None = None,
    show_plot: bool = True,
) -> None:
    # Calculate layout dimensions
    num_metrics = len(metrics)
    num_recipes = len(recipes)
    figwidth = max(12, num_recipes * 4)
    figheight = max(6, num_metrics * 3)

    # Create nice metric labels
    metric_labels = {
        "pile-valppl": "Pile Validation Perplexity",
        "mmlu_average_acc_raw": "MMLU Average Accuracy",
        "mmlu_average_correct_prob": "MMLU Average Correct Probability",
        "arc_challenge_acc_raw": "ARC Challenge Accuracy",
        "hellaswag_acc_raw": "HellaSwag Accuracy",
    }

    # Use df's metric column to create metric_label if needed
    if "metric_label" not in df.columns and "metric" in df.columns:
        df["metric_label"] = df["metric"].map(lambda m: metric_labels.get(m, m))

    with FigureManager(
        PlotConfig(
            layout={
                "rows": num_metrics,
                "cols": num_recipes,
                "figsize": (figwidth, figheight),
                "tight_layout_pad": 0.5,
                "subplot_kwargs": {"sharey": "row"},
            },
            legend=LegendConfig(
                strategy="figure",
                ncol=min(len(model_sizes), 4),
                layout_bottom_margin=0.15,
            ),
        )
    ) as fm:
        fm.fig.suptitle(
            "DataDecide Visualization: Metrics x Data Recipes",
            fontsize=16,
            y=0.98,
        )

        # Create faceting configuration
        faceting = FacetingConfig(
            rows="metric",  # Metrics across rows
            cols="data",  # Data recipes across columns
            lines="params",  # Model sizes as different lines
            x="step",
            y="value",
            row_order=metrics,
            col_order=recipes,
            lines_order=model_sizes,
        )

        # Plot with one call using faceting system
        fm.plot_faceted(
            data=df,
            plot_type="line",
            faceting=faceting,
            linewidth=1.5,
            alpha=0.8,
        )

        # Format axes
        for row_idx in range(num_metrics):
            for col_idx in range(num_recipes):
                ax = fm.get_axes(row_idx, col_idx)

                # Set labels only where needed
                if row_idx == num_metrics - 1:  # Bottom row
                    ax.set_xlabel("Training Steps")
                else:
                    ax.set_xlabel("")

                if col_idx == 0:  # Left column
                    # Get metric label from the data
                    metric = metrics[row_idx]
                    metric_label = metric_labels.get(metric, metric)
                    ax.set_ylabel(metric_label)
                else:
                    ax.set_ylabel("")

                # Set recipe title on top row only
                if row_idx == 0:
                    ax.set_title(recipes[col_idx], pad=10)

                # Apply axis scales
                if x_log:
                    ax.set_xscale("log")
                else:
                    ax.ticklabel_format(style="scientific", axis="x", scilimits=(0, 0))

                if y_log:
                    ax.set_yscale("log")

                # Apply axis limits if specified
                if xlim:
                    ax.set_xlim(xlim)

                if ylim:
                    ax.set_ylim(ylim)

                # Add grid for readability
                ax.grid(visible=True, alpha=0.3)

    # Save or display plot
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Plot saved to: {save_path}")

    if show_plot:
        plt.show()

    if not show_plot and not save_path:
        print(
            "Warning: Plot not saved or displayed. Use --save-path or remove --no-show"
        )


def main() -> None:
    parser = create_arg_parser()
    args = parser.parse_args()

    print("Initializing DataDecide with streamlined API...")
    try:
        # Get DataDecide instance with one call
        dd = DataDecide()

        # Validate user inputs directly through dd methods
        metrics = args.metrics
        model_sizes = dd.select_params(args.model_sizes)
        recipes = dd.select_data(args.recipes)

        print(f"Selected metrics: {metrics}")
        print(f"Selected model sizes: {model_sizes}")
        print(f"Selected data recipes: {recipes}")

        # Prepare plot data with one call using smart filtering and auto melting
        print("Preparing data with unified preparation pipeline...")
        df = dd.prepare_plot_data(
            params=model_sizes,
            data=recipes,
            metrics=metrics,
            aggregate_seeds=args.aggregate_seeds,
            auto_filter=True,  # Smart filtering based on metrics
            melt=True,  # Auto-converts to long format for plotting
        )
        print(f"Prepared {len(df)} data points for plotting")

        # Create the plot
        print("Creating faceted visualization...")
        create_faceted_plot(
            df=df,
            metrics=metrics,
            recipes=recipes,
            model_sizes=model_sizes,
            x_log=args.x_log,
            y_log=args.y_log,
            xlim=args.xlim,
            ylim=args.ylim,
            save_path=args.save_path,
            show_plot=not args.no_show,
        )
        print("Visualization complete!")

    except ImportError as e:
        print(f"Error: {e}")
        print("DataDecide integration requires the 'datadec' optional dependency.")
        print("Install with: uv add 'dr_plotter[datadec]'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
