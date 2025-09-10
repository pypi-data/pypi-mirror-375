from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import click
import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter import consts
from dr_plotter.configs import PlotConfig
from dr_plotter.scripting import (
    CLIConfig,
    build_configs,
    validate_layout_options,
    validate_unused_parameters,
)


def show_or_save_plot(
    fig: Any, save_dir: str | None, pause_duration: int, filename: str
) -> None:
    if save_dir:
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        savename = save_path / f"{filename}.png"
        fig.savefig(savename, dpi=300)
        print(f"Plot saved to {savename}")
    else:
        plt.show(block=False)
        plt.pause(pause_duration)

    plt.close(fig)


def create_and_render_plot(
    ax: Any, plotter_class: Any, plotter_args: Any, **kwargs: Any
) -> None:
    plotter = plotter_class(*plotter_args, **kwargs)
    plotter.render(ax)


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


def parse_scale_flags(scale_str: str) -> tuple[bool, bool]:
    x_scale, y_scale = parse_scale_pair(scale_str)
    return x_scale == "log", y_scale == "log"


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


def load_dataset(file_path: str) -> pd.DataFrame:
    path = Path(file_path).expanduser()
    assert path.suffix == ".parquet", "Only parquet files are supported"
    assert path.exists(), f"Dataset not found: {path}"
    df = pd.read_parquet(path)
    return df


def validate_columns(df: pd.DataFrame, merged_args: Any) -> None:
    column_options = [(key, merged_args.get(key)) for key in consts.COLUMN_KEYS]
    for option_name, column_name in column_options:
        if column_name and column_name not in df.columns:
            available_cols = ", ".join(sorted(df.columns))
            raise click.UsageError(
                f"Column '{column_name}' for --{option_name} "
                f"not found in dataset. Available columns: {available_cols}"
            )


def validate_args(
    df: pd.DataFrame,
    merged_args: dict[str, Any],
    unused_kwargs: dict[str, Any],
    workflow_config: CLIWorkflowConfig,
) -> None:
    validate_layout_options(click.get_current_context(), **merged_args)
    validate_unused_parameters(unused_kwargs, workflow_config.allowed_unused)
    validate_columns(df, merged_args)


def apply_fixed_params(
    merged_args: dict[str, Any], workflow_config: CLIWorkflowConfig
) -> dict[str, Any]:
    for param, value in workflow_config.fixed_params.items():
        assert param not in merged_args, (
            f"Param: {param} is fixed and cannot be overridden"
        )
        merged_args[param] = value
    return merged_args


@dataclass
class CLIWorkflowConfig:
    data_loader: Callable[[dict], pd.DataFrame]
    default_params: dict[str, Any] = field(default_factory=dict)
    fixed_params: dict[str, Any] = field(default_factory=dict)
    allowed_unused: set[str] | None = None


def execute_cli_workflow(
    kwargs: dict[str, Any], workflow_config: CLIWorkflowConfig
) -> tuple[pd.DataFrame, PlotConfig]:
    config = CLIConfig.load_or_default(kwargs)
    merged_args = {**workflow_config.default_params}
    merged_args.update(config.merge_with_cli_args(kwargs))
    merged_args = apply_fixed_params(merged_args, workflow_config)

    plot_config, unused_kwargs = build_configs(merged_args)
    df = workflow_config.data_loader(merged_args)
    validate_args(df, merged_args, unused_kwargs, workflow_config)

    return df, plot_config
