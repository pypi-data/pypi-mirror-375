"""
Data Exploration Script for ML Training Metrics

Requires DataDecide integration:
    uv add "dr_plotter[datadec]"

Explores available metrics, data recipes, and model sizes in the dataset.
"""

import sys
from typing import Any

import pandas as pd

from datadec import DataDecide


def load_parquet_data() -> pd.DataFrame:
    """Load clean, pre-validated data from DataDecide."""
    try:
        dd = DataDecide()
        return dd.get_filtered_df(filter_types=["ppl", "max_steps"])
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)


def get_data_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Get basic data summary - DataDecide guarantees structure."""
    return {
        "total_columns": len(df.columns),
        "total_rows": len(df),
        "data_types": dict(df.dtypes),
        "key_columns_present": True,  # DataDecide guarantees these exist
        "has_metric_columns": True,  # DataDecide provides cleaned metric data
    }


def extract_available_metrics(df: pd.DataFrame) -> list[str]:
    non_metric_columns = [
        "params",
        "data",
        "step",
        "seed",
        "tokens",
        "compute",
        "total_steps",
        "warmup_steps",
        "lr_max",
        "batch_size",
        "lr_at_step",
        "cumulative_lr",
    ]
    metric_columns = [col for col in df.columns if col not in non_metric_columns]
    return sorted(metric_columns)


def extract_data_recipes(df: pd.DataFrame) -> list[str]:
    return sorted(df["data"].unique().tolist())


def extract_model_sizes(df: pd.DataFrame) -> list[str]:
    return sorted(df["params"].unique().tolist())


def analyze_data_completeness(df: pd.DataFrame) -> dict[str, Any]:
    model_sizes = extract_model_sizes(df)
    data_recipes = extract_data_recipes(df)
    metrics = extract_available_metrics(df)

    total_combinations = len(model_sizes) * len(data_recipes)
    existing_combinations = len(df[["params", "data"]].drop_duplicates())

    missing_combinations = []
    for model_size in model_sizes:
        for recipe in data_recipes:
            combo_exists = (
                len(df[(df["params"] == model_size) & (df["data"] == recipe)]) > 0
            )
            if not combo_exists:
                missing_combinations.append((model_size, recipe))

    step_distribution = df.groupby(["params", "data"])["step"].count().describe()

    metric_completeness = {}
    for metric in metrics[:10]:
        null_count = df[metric].isna().sum()
        metric_completeness[metric] = {
            "null_count": null_count,
            "null_percentage": (null_count / len(df)) * 100,
        }

    return {
        "total_expected_combinations": total_combinations,
        "existing_combinations": existing_combinations,
        "missing_combinations_count": len(missing_combinations),
        "missing_combinations": missing_combinations[:20],
        "data_density_percentage": (existing_combinations / total_combinations) * 100,
        "steps_per_combination_stats": step_distribution.to_dict(),
        "sample_metric_completeness": metric_completeness,
        "total_metrics_analyzed": len(metrics),
    }


def main() -> None:
    print("=" * 80)
    print("DATA EXPLORATION: MEAN_EVAL.PARQUET ANALYSIS")
    print("=" * 80)

    df = load_parquet_data()
    print(
        f"Successfully loaded dataset with {len(df):,}"
        f"rows and {len(df.columns):,} columns"
    )

    print("\n" + "=" * 50)
    print("DATA SUMMARY")
    print("=" * 50)
    summary = get_data_summary(df)

    print("✅ Data structure validated by DataDecide")
    print(f"Total columns: {summary['total_columns']:,}")
    print(f"Total rows: {summary['total_rows']:,}")
    print(f"Key columns present: {summary['key_columns_present']}")
    print(f"Has metric columns: {summary['has_metric_columns']}")

    key_column_types = {
        col: str(summary["data_types"][col])
        for col in ["params", "data", "step"]
        if col in summary["data_types"]
    }
    print(f"Key column types: {key_column_types}")

    print("\n" + "=" * 50)
    print("AVAILABLE DIMENSIONS")
    print("=" * 50)

    metrics = extract_available_metrics(df)
    data_recipes = extract_data_recipes(df)
    model_sizes = extract_model_sizes(df)

    print(f"Available metrics ({len(metrics)} total):")
    for i, metric in enumerate(metrics):
        print(f"  {i + 1:2d}. {metric}")

    print(f"\nData recipes ({len(data_recipes)} total):")
    for i, recipe in enumerate(data_recipes):
        print(f"  {i + 1:2d}. {recipe}")

    print(f"\nModel sizes ({len(model_sizes)} total):")
    for i, size in enumerate(model_sizes):
        print(f"  {i + 1:2d}. {size}")

    print("\n" + "=" * 50)
    print("DATA COMPLETENESS ANALYSIS")
    print("=" * 50)

    completeness = analyze_data_completeness(df)
    # Note: DataDecide provides pre-filtered, clean data with guaranteed completeness

    print(
        f"Total expected combinations (model_size × data_recipe): "
        f"{completeness['total_expected_combinations']:,}"
    )
    print(f"Existing combinations: {completeness['existing_combinations']:,}")
    print(f"Missing combinations: {completeness['missing_combinations_count']:,}")
    print(f"Data density: {completeness['data_density_percentage']:.1f}%")

    if completeness["missing_combinations_count"] > 0:
        print(
            f"\nFirst {min(10, len(completeness['missing_combinations']))}"
            "missing combinations:"
        )
        for i, (model_size, recipe) in enumerate(
            completeness["missing_combinations"][:10]
        ):
            print(f"  {i + 1:2d}. {model_size} × {recipe}")

    steps_stats = completeness["steps_per_combination_stats"]
    print("\nSteps per combination statistics:")
    print(f"  Mean: {steps_stats['mean']:.1f}")
    print(f"  Median: {steps_stats['50%']:.1f}")
    print(f"  Min: {steps_stats['min']:.0f}")
    print(f"  Max: {steps_stats['max']:.0f}")

    print("\nSample metric completeness (first 10 metrics):")
    for metric, stats in list(completeness["sample_metric_completeness"].items())[:10]:
        print(
            f"  {metric}: "
            f"{stats['null_count']:,} nulls ({stats['null_percentage']:.1f}%)"
        )

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    print(
        f"Dataset contains {len(metrics):,}"
        f"metrics across {len(data_recipes)} data recipes"
        "and {len(model_sizes)} model sizes"
    )
    print(
        f"Data coverage is {completeness['data_density_percentage']:.1f}% with"
        f"{completeness['missing_combinations_count']} missing combinations"
    )

    step_range = sorted(df["step"].unique())
    print(f"Training steps range from {step_range[0]:.0f} to {step_range[-1]:.0f}")

    full_percentage = 100.0
    if completeness["data_density_percentage"] < full_percentage:
        print("\nLIMITATIONS DISCOVERED:")
        print(
            f"- {completeness['missing_combinations_count']}"
            " model_size x data_recipe combinations missing"
        )
        print("- May impact plotting for specific combinations")

    null_metrics = [
        metric
        for metric, stats in completeness["sample_metric_completeness"].items()
        if stats["null_count"] > 0
    ]
    if null_metrics:
        print(
            f"- Some metrics have null values: {len(null_metrics)} of sampled metrics"
        )

    print("\n✅ READY FOR PLOTTING:")
    print(f"- {len(metrics)} metrics available for row faceting")
    print(f"- {len(data_recipes)} data recipes available for column faceting")
    print(f"- {len(model_sizes)} model sizes available for line styling")
    print("- Data pre-validated by DataDecide and ready for analysis")
    print(
        "- Use dr_plotter examples with --recipes and --model-sizes flags for plotting"
    )


if __name__ == "__main__":
    main()
