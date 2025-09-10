from __future__ import annotations

import ast
from typing import Any

import matplotlib.pyplot as plt


def get_axes_from_grid(
    axes: plt.Axes, row: int | None = None, col: int | None = None
) -> plt.Axes:
    if not hasattr(axes, "__len__"):
        return axes

    if not hasattr(axes, "ndim") and len(axes) > 0:
        first_ax = axes[0]
        assert (
            hasattr(first_ax, "get_gridspec") and first_ax.get_gridspec() is not None
        ), "Cannot determine grid dimensions: first axis has no gridspec"

        gs = first_ax.get_gridspec()
        nrows, ncols = gs.nrows, gs.ncols

        assert row is not None and col is not None, (
            "Must specify both row and col for list-based axes"
        )
        linear_index = row * ncols + col
        assert linear_index < len(axes), (
            f"Index {linear_index} (row={row}, col={col}) "
            f"out of bounds for {len(axes)} axes"
        )
        return axes[linear_index]

    if hasattr(axes, "ndim") and axes.ndim == 1:
        if len(axes) > 1:
            first_ax = axes[0]
            if (
                hasattr(first_ax, "get_gridspec")
                and first_ax.get_gridspec() is not None
            ):
                gs = first_ax.get_gridspec()
                nrows, ncols = gs.nrows, gs.ncols

                if ncols == 1 and nrows > 1:
                    assert row is not None, "Must specify row for vertical grid layout"
                    return axes[row]
                elif nrows == 1 and ncols > 1:
                    assert col is not None, (
                        "Must specify col for horizontal grid layout"
                    )
                    return axes[col]
        idx = col if col is not None else row
        assert idx is not None, "Must specify either row or col for 1D axes array"
        return axes[idx]

    if row is not None and col is not None:
        return axes[row, col]
    elif row is not None:
        return axes[row, :]
    elif col is not None:
        return axes[:, col]

    return axes


def parse_scale_pair(scale_str: str) -> tuple[str, str]:
    scale_map = {"lin": "linear", "linear": "linear", "log": "log"}

    # Handle concatenated format (linlin, linlog, loglin, loglog)
    if "-" not in scale_str:
        if scale_str == "linlin":
            return "linear", "linear"
        elif scale_str == "linlog":
            return "linear", "log"
        elif scale_str == "loglin":
            return "log", "linear"
        elif scale_str == "loglog":
            return "log", "log"
        else:
            raise ValueError(f"Unknown concatenated scale format: '{scale_str}'")

    # Handle hyphenated format (lin-lin, linear-log, etc.)
    x_scale, y_scale = scale_str.split("-", 1)

    assert x_scale in scale_map, f"Unknown x scale: '{x_scale}'"
    assert y_scale in scale_map, f"Unknown y scale: '{y_scale}'"

    return scale_map[x_scale], scale_map[y_scale]


def parse_key_value_args(args: list[str] | None) -> dict[str, Any]:
    result = {}
    if not args:
        return result
    for arg in args:
        assert "=" in arg, f"Invalid format: {arg}. Use key=value"
        key, value = arg.split("=", 1)
        key = key.strip()
        values = [v.strip() for v in value.split(",")]
        rk = [_convert_to_number_if_numeric(v) for v in values]
        result[key] = rk if "," in arg else rk[0]
    return result


def _convert_to_number_if_numeric(value: str) -> Any:
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)
    if _is_float_string(value):
        return float(value)
    return value


def convert_cli_value_to_type(value: Any, target_type: type) -> Any:
    if not isinstance(value, str):
        return value

    if target_type is bool:
        return value.lower() in ("true", "1", "yes", "on")
    elif target_type is int:
        return int(value)
    elif target_type is float:
        return float(value)
    elif target_type is str:
        return value
    else:
        try:
            return ast.literal_eval(value)
        except Exception:
            return value


def _is_float_string(value: str) -> bool:
    if not value:
        return False
    check_value = value[1:] if value.startswith("-") else value
    if "." not in check_value:
        return False
    parts = check_value.split(".")
    num_parts_in_float = 2
    if len(parts) != num_parts_in_float:
        return False
    return all(part.isdigit() or part == "" for part in parts) and any(
        part for part in parts
    )
