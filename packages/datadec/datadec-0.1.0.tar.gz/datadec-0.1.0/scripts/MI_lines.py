from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from dr_plotter import FigureManager
from dr_plotter.configs import PlotConfig

from datadec import DataDecide

dd = DataDecide()


def normalize_df(df: pd.DataFrame, params: list[str], data: list[str]) -> pd.DataFrame:
    # For each (params, data) group, get the row with the minimum tokens
    # (and all columns)
    idx_min = df.groupby(["params", "data"])["tokens"].idxmin()
    idx_max = df.groupby(["params", "data"])["tokens"].idxmax()
    df_pd_min = (
        df.loc[idx_min]
        .reset_index(drop=True)
        .rename(
            columns={
                "tokens": "min_tokens",
                "value": "min_step_value",
                "step": "min_step",
            },
        )
    )
    df_pd_max = (
        df.loc[idx_max]
        .reset_index(drop=True)
        .rename(
            columns={
                "tokens": "max_tokens",
                "value": "max_step_value",
                "step": "max_step",
            },
        )
    )
    df = df.merge(df_pd_min, on=["params", "data"], how="left")
    df = df.merge(df_pd_max, on=["params", "data"], how="left")
    df["normed_value"] = df["value"] / df["min_step_value"]
    df["normed_centered_value"] = 1 - (df["value"] / df["min_step_value"])
    df["normed_x"] = df["tokens"] / df["max_tokens"]
    return df


def main() -> Any:
    for c in dd.full_eval.columns:
        print(c)
    params = dd.select_params(["20M", "60M", "90M", "530M"])
    data = dd.select_data("Dolma1.7")
    metric = "pile-valppl"
    metrics = [metric]
    df = dd.prepare_plot_data(
        params=params, data=data, metrics=metrics, aggregate_seeds=True
    )
    df = normalize_df(df, params, data)
    print(df.head())

    y_val = "normed_centered_value"

    with FigureManager(
        PlotConfig(
            layout={"rows": 2, "cols": 4, "figsize": (16, 10), "tight_layout_pad": 1.0}
        )
    ) as fm:
        fm.fig.suptitle(f"{metric} for {data}", fontsize=16)
        # Multiple lines with hue
        fm.plot(
            "line",
            0,
            0,
            df,
            x="tokens",
            y=y_val,
            hue_by="params",
            title="lin-lin x=tokens",
            xlabel="Tokens",
            ylabel="PPL",
        )
        fm.plot(
            "line",
            0,
            1,
            df,
            x="tokens",
            y=y_val,
            hue_by="params",
            title="lin-log x=tokens",
            xlabel="Tokens",
            ylabel="PPL (log scale)",
        )
        fm.plot(
            "line",
            0,
            2,
            df,
            x="tokens",
            y=y_val,
            hue_by="params",
            title="log-lin x=tokens",
            xlabel="Tokens (log scale)",
            ylabel="PPL",
        )
        fm.plot(
            "line",
            0,
            3,
            df,
            x="tokens",
            y=y_val,
            hue_by="params",
            title="log-log x=tokens",
            xlabel="Tokens (log scale)",
            ylabel="PPL (log scale)",
        )
        # fm.get_axes(0, 0).set_xscale("log")
        # fm.get_axes(0, 0).set_yscale("log")

        # fm.get_axes(0, 1).set_xscale("log")
        fm.get_axes(0, 1).set_yscale("log")

        fm.get_axes(0, 2).set_xscale("log")
        # fm.get_axes(0, 2).set_yscale("log")

        fm.get_axes(0, 3).set_xscale("log")
        fm.get_axes(0, 3).set_yscale("log")
        # fm.get_axes(0, 1).set_ylim(0, 1)
        # fm.get_axes(0, 2).set_ylim(0, 1)
        """
        fm.plot(
            "line",
            0,
            0,
            df,
            x="tokens",
            y="value",
            hue_by="params",
            title=f"{metric} for {data}",
            xlabel="Tokens (log scale)",
            ylabel="PPL",
        )
        fm.plot(
            "line",
            0,
            1,
            df,
            x="tokens",
            y="normed_centered_value",
            hue_by="params",
            title=f"{metric} for {data}",
            xlabel="Tokens (log scale)",
            ylabel="PPL (normalized centered)",
        )
        fm.plot(
            "line",
            0,
            2,
            df,
            x="tokens",
            y="normed_centered_value",
            hue_by="params",
            title=f"{metric} for {data}",
            xlabel="Tokens (log scale)",
            ylabel="PPL (normalized centered, log scale)",
        )
        fm.get_axes(0, 0).set_xscale("log")
        fm.get_axes(0, 1).set_xscale("log")
        fm.get_axes(0, 2).set_xscale("log")
        fm.get_axes(0, 2).set_yscale("log")
        fm.get_axes(0, 1).set_ylim(0, 1)
        fm.get_axes(0, 2).set_ylim(0, 1)
        """
        # fm.get_axes(0, 1).set_xscale("log")
        # fm.get_axes(0, 2).set_xscale("log")
        fm.plot(
            "line",
            1,
            0,
            df,
            x="normed_x",
            y=y_val,
            hue_by="params",
            title="lin-lin x=% training",
            xlabel="% of training tokens",
            ylabel="PPL",
        )
        fm.plot(
            "line",
            1,
            1,
            df,
            x="normed_x",
            y=y_val,
            hue_by="params",
            title="lin-log x=% training",
            xlabel="% of training tokens",
            ylabel="PPL (log scale)",
        )
        fm.plot(
            "line",
            1,
            2,
            df,
            x="normed_x",
            y=y_val,
            hue_by="params",
            title="log-lin x=% training",
            xlabel="% of training tokens (log scale)",
            ylabel="PPL",
        )
        fm.plot(
            "line",
            1,
            3,
            df,
            x="normed_x",
            y=y_val,
            hue_by="params",
            title="log-log x=% training",
            xlabel="% of training tokens (log scale)",
            ylabel="PPL (log scale)",
        )
        # fm.get_axes(1, 0).set_yscale("log")
        # fm.get_axes(1, 0).set_xscale("log")

        # fm.get_axes(1, 1).set_xscale("log")
        fm.get_axes(1, 1).set_yscale("log")

        fm.get_axes(1, 2).set_xscale("log")
        # fm.get_axes(1, 2).set_yscale("log")

        fm.get_axes(1, 3).set_yscale("log")
        fm.get_axes(1, 3).set_xscale("log")

        # fm.get_axes(1, 1).set_ylim(0, 1)
        # fm.get_axes(1, 2).set_ylim(0, 1)
        """
        fm.plot(
            "line",
            1,
            0,
            df,
            x="normed_x",
            y="value",
            hue_by="params",
            title=f"{metric} for {data}",
            xlabel="% of training tokens (log scale)",
            ylabel="PPL (log scale)",
        )
        fm.plot(
            "line",
            1,
            1,
            df,
            x="normed_x",
            y="normed_centered_value",
            hue_by="params",
            title=f"{metric} for {data}",
            xlabel="% of training tokens",
            ylabel="PPL (normalized centered)",
        )
        fm.plot(
            "line",
            1,
            2,
            df,
            x="normed_x",
            y="normed_centered_value",
            hue_by="params",
            title=f"{metric} for {data}",
            xlabel="% of training tokens (log scale)",
            ylabel="PPL (normalized centered (log scale))",
        )
        fm.get_axes(1, 0).set_yscale("log")
        fm.get_axes(1, 0).set_xscale("log")
        fm.get_axes(1, 2).set_yscale("log")
        fm.get_axes(1, 2).set_xscale("log")
        #fm.get_axes(1, 1).set_xscale("log")
        #fm.get_axes(1, 2).set_xscale("log")
        fm.get_axes(1, 1).set_ylim(0, 1)
        fm.get_axes(1, 2).set_ylim(0, 1)
        """

    plt.show()


if __name__ == "__main__":
    main()
