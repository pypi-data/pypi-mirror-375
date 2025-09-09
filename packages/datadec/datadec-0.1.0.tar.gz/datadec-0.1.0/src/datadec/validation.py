from typing import List, Optional, Union

from datadec import constants as consts

FILTER_TYPES = ["max_steps", "ppl", "olmes"]
METRIC_TYPES = ["ppl", "olmes"]


def _choices_valid(choices: Union[str, List[str]], valid_options: List[str]) -> bool:
    if choices == "all":
        return True
    choice_list = [choices] if isinstance(choices, str) else choices
    return all(choice in valid_options for choice in choice_list)


def _select_choices(
    choices: Union[str, List[str]],
    valid_options: List[str],
    exclude: Optional[List[str]] = None,
) -> List[str]:
    exclude = exclude or []
    if choices == "all":
        selected = [choice for choice in valid_options if choice not in exclude]
    else:
        choice_list = set([choices] if isinstance(choices, str) else choices)
        selected = [choice for choice in choice_list if choice not in exclude]
    return selected


def validate_filter_types(filter_types: List[str]) -> None:
    """Validate filter types against known options."""
    assert all(filter_type in FILTER_TYPES for filter_type in filter_types), (
        f"Invalid filter types: {filter_types}. Available: {FILTER_TYPES}"
    )


def validate_metric_type(metric_type: Optional[str]) -> None:
    """Validate metric type against known options."""
    if metric_type is not None:
        assert metric_type in METRIC_TYPES, (
            f"Unknown metric_type '{metric_type}'. Available: {METRIC_TYPES}"
        )


def validate_metrics(metrics: List[str]) -> None:
    """Validate metric names against known options."""
    assert all(metric in consts.ALL_KNOWN_METRICS for metric in metrics), (
        f"Unknown metrics: {metrics}. Available: {consts.ALL_KNOWN_METRICS}"
    )


def _validated_select(
    choices: Union[str, List[str]],
    valid_options: List[str],
    name: str,
    exclude: Optional[List[str]] = None,
) -> List[str]:
    """Generic validated selection utility."""
    assert _choices_valid(choices, valid_options), (
        f"Invalid {name}. Available: {valid_options}"
    )
    return _select_choices(
        choices=choices,
        valid_options=valid_options,
        exclude=exclude,
    )


def determine_filter_types(metrics: List[str]) -> List[str]:
    filter_types = ["max_steps"]

    ppl_metrics_filtered = [m for m in metrics if m in consts.PPL_TYPES]
    olmes_metrics_filtered = [m for m in metrics if m not in consts.PPL_TYPES]

    if ppl_metrics_filtered and not olmes_metrics_filtered:
        filter_types.append("ppl")
    elif olmes_metrics_filtered and not ppl_metrics_filtered:
        filter_types.append("olmes")

    return filter_types
