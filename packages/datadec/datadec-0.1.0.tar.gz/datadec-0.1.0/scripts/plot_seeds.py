import math
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt

from datadec import DataDecide
from datadec.constants import PPL_TYPES
from dr_plotter import FigureManager
from dr_plotter.configs import LegendConfig, LegendStrategy, PlotConfig, LayoutConfig


def get_data_param_combos(
    dd: DataDecide, recipe=None, param=None
) -> List[Tuple[str, str]]:
    params = param if param is not None else "all"
    recipes = recipe if recipe is not None else "all"
    return [(d, p) for d in dd.select_data(recipes) for p in dd.select_params(params)]


def plot_seeds(
    dd: DataDecide, num_cols: int, metrics: List[str], recipe=None, param=None
) -> None:
    data_param_combos = get_data_param_combos(dd, recipe, param)
    combinations = [(p, r, m) for r, p in data_param_combos for m in metrics]
    num_rows = math.ceil(len(combinations) / num_cols)

    with FigureManager(
        config=PlotConfig(
            layout=LayoutConfig(
                rows=num_rows, cols=num_cols, figsize=(num_cols * 6, num_rows * 4)
            )
        )
    ) as fm:
        for i, (param_val, recipe_val, metric) in enumerate(combinations):
            row = i // num_cols
            col = i % num_cols

            subset = dd.select_subset(
                dd.full_eval, params=[param_val], data=[recipe_val]
            )

            fm.plot(
                "line",
                row,
                col,
                subset,
                x="tokens",
                y=metric,
                hue_by="seed",
                title=f"{param_val} | {recipe_val} | {metric}",
            )
    plt.show()


def plot_overlay(
    dd: DataDecide,
    metrics: List[str],
    num_cols: int,
    recipe=None,
    param=None,
    save_dir=None,
) -> None:
    data_param_combos = get_data_param_combos(dd, recipe, param)
    num_rows = math.ceil(len(data_param_combos) / num_cols)

    # Use unified plotting preparation - replaces manual filtering and melting!
    melted_df = dd.prepare_plot_data(
        params=param if param is not None else "all",
        data=recipe if recipe is not None else "all",
        metrics=metrics,
        aggregate_seeds=False,
    )

    # Create x_labels and y_labels arrays
    x_labels = [
        ["Tokens"] * num_cols if row == num_rows - 1 else [None] * num_cols
        for row in range(num_rows)
    ]
    y_labels = [
        ["Perplexity" if col == 0 else None for col in range(num_cols)]
        for row in range(num_rows)
    ]

    with FigureManager(
        config=PlotConfig(
            layout=LayoutConfig(
                rows=num_rows,
                cols=num_cols,
                figsize=(num_cols * 6, num_rows * 6),
                x_labels=x_labels,
                y_labels=y_labels,
                tight_layout_pad=1.0,
            ),
            legend=LegendConfig(
                strategy=LegendStrategy.GROUPED_BY_CHANNEL,
                channel_titles={"hue": "Val Dataset (for PPL calc)", "alpha": "Seed"},
                layout_bottom_margin=0.22,
                bbox_y_offset=0.22,
                ncol=4,
                two_legend_left_x=0.1,
                two_legend_right_x=0.5,
            ),
        )
    ) as fm:
        for i, (data_val, param_val) in enumerate(data_param_combos):
            row = i // num_cols
            col = i % num_cols

            subset = melted_df[
                (melted_df["data"] == data_val) & (melted_df["params"] == param_val)
            ]

            fm.plot(
                "line",
                row,
                col,
                subset,
                x="tokens",
                y="value",
                hue_by="metric",
                alpha_by="seed",
                title=f"{data_val} | {param_val}",
            )

        # Set ylim for all subplots based on recipe
        recipe_ylims = {
            "C4": 225,
            "DCLM-Baseline": 60,
            "Dolma1.7": 60,
            "FineWeb-Edu": 100,
        }
        ylim_max = recipe_ylims.get(recipe, 225)  # Default to 225 if recipe not found

        for ax in fm.fig.axes:
            ax.set_ylim(0, ylim_max)
            ax.set_xlim(0, 3.1e10)

    if save_dir:
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        filename = f"{recipe}_ppl_metrics_per_seed.png"
        filepath = save_path / filename
        fm.fig.savefig(filepath, dpi=150, bbox_inches="tight")
        print(f"Saved plot to: {filepath}")
    else:
        plt.show()


def main():
    dd = DataDecide()
    save_dir = "/Users/daniellerothermel/drotherm/repos/datadec/outputs/plots"
    ncols = 3
    recipes = ["C4", "DCLM-Baseline", "Dolma1.7", "FineWeb-Edu"]
    params = ["90M", "150M", "300M"]

    for recipe in recipes:
        print(f"Generating plot for recipe: {recipe}")
        plot_overlay(
            dd=dd,
            metrics=PPL_TYPES,
            num_cols=ncols,
            recipe=recipe,
            param=params,
            save_dir=save_dir,
        )


if __name__ == "__main__":
    main()
