from __future__ import annotations

import math

import pandas as pd

from dr_plotter.configs import FacetingConfig
from dr_plotter.faceting.dimensional_utils import resolve_dimension_values


def calculate_auto_sizing(
    config: FacetingConfig,
    grid_shape: tuple[int, int],
) -> tuple[float, float]:
    return config.subplot_width * grid_shape[1], config.subplot_height * grid_shape[0]


def calculate_wrapped_grid(
    values: list[str], max_cols: int | None, max_rows: int | None
) -> tuple[int, int]:
    n_values = len(values)
    if max_cols:
        n_rows = math.ceil(n_values / max_cols)
        n_cols = max_cols
    elif max_rows:
        n_rows = max_rows
        n_cols = math.ceil(n_values / max_rows)
    else:
        n_rows = 1
        n_cols = n_values
    return n_rows, n_cols


def get_grid_dimensions(data: pd.DataFrame, config: FacetingConfig) -> tuple[int, int]:
    assert not data.empty, "Cannot compute dimensions from empty DataFrame"
    if config.target_row is not None and config.target_col is not None:
        return max(config.target_row + 1, 1), max(config.target_col + 1, 1)
    if config.wrap_by:
        values = resolve_dimension_values(data, config.wrap_by, config)
        return calculate_wrapped_grid(values, config.max_cols, config.max_rows)
    row_values = (
        resolve_dimension_values(data, config.rows_by, config)
        if config.rows_by
        else [None]
    )
    col_values = (
        resolve_dimension_values(data, config.cols_by, config)
        if config.cols_by
        else [None]
    )
    n_rows = len(row_values)
    n_cols = len(col_values)
    return n_rows, n_cols
