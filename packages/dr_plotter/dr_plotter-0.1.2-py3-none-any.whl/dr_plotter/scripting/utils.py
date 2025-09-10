from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

import click
import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter import consts
from dr_plotter.scripting.cli_framework import (
    CLIConfig,
    build_configs,
    validate_layout_options,
    validate_unused_parameters,
)

if TYPE_CHECKING:
    from dr_plotter.configs import PlotConfig


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
