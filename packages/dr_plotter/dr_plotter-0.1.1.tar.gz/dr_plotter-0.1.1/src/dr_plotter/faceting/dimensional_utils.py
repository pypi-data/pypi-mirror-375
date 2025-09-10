from __future__ import annotations

import re
from typing import Any

import pandas as pd

from dr_plotter.configs import FacetingConfig


def smart_sort_key(value: Any) -> tuple[float, str]:
    str_value = str(value)
    match = re.match(r"^(\d+(?:\.\d+)?)([A-Za-z]*)$", str_value.strip())
    if match:
        numeric_part = float(match.group(1))
        unit_part = match.group(2).upper()
        unit_multipliers = {
            "K": 1e3,
            "M": 1e6,
            "B": 1e9,
            "T": 1e12,
            "KB": 1e3,
            "MB": 1e6,
            "GB": 1e9,
            "TB": 1e12,
        }
        multiplier = unit_multipliers.get(unit_part, 1)
        return (numeric_part * multiplier, str_value)
    return (float("inf"), str_value)


def smart_sort_values(values: list[Any]) -> list[Any]:
    return sorted(values, key=smart_sort_key)


def apply_dimensional_filters(
    data: pd.DataFrame, config: FacetingConfig
) -> pd.DataFrame:
    for attr, op in [
        ("fixed", lambda d, v: d == v),
        ("order", lambda d, v: d.isin(v)),
        ("exclude", lambda d, v: ~d.isin(v)),
    ]:
        values = getattr(config, attr, None)
        if values:
            for dim, val in values.items():
                if dim in data.columns:
                    data = data[op(data[dim], val)]
    return data


def resolve_dimension_values(
    data: pd.DataFrame,
    dim: str,
    config: FacetingConfig,
) -> list[str]:
    if getattr(config, "fixed", None) and dim in config.fixed:
        return [config.fixed[dim]]
    vals = (
        config.order[dim]
        if getattr(config, "order", None) and dim in config.order
        else smart_sort_values(data[dim].unique())
    )
    if getattr(config, "exclude", None) and dim in config.exclude:
        exclude_set = set(config.exclude[dim])
        vals = [v for v in vals if v not in exclude_set]
    return vals


def generate_dimensional_title(config: FacetingConfig) -> str:
    if config.fixed:
        return " ".join(f"{k}={v}" for k, v in config.fixed.items())
    return f"{config.y} by {config.x}"
