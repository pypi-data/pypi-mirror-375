from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from dr_plotter import FigureManager
from dr_plotter.scripting import (
    CLIWorkflowConfig,
    dimensional_plotting_cli,
    execute_cli_workflow,
    load_dataset,
)
from dr_plotter.scripting.utils import show_or_save_plot
from dr_plotter.theme import BASE_THEME, FigureStyles, Theme

CLI_THEME = Theme(
    name="dr_plotter_cli",
    parent=BASE_THEME,
    figure_styles=FigureStyles(
        legend_position=(0.5, 0.02),
        multi_legend_positions=[(0.3, 0.02), (0.7, 0.02)],
        subplot_width=3.5,
        subplot_height=3.0,
        row_title_rotation=90,
        legend_frameon=True,
        legend_tight_layout_rect=(0, 0.08, 1, 1),
    ),
)


@click.command()
@click.argument("dataset_path", type=click.Path())
@click.option(
    "--x",
    required=True,
    help="Column name for x-axis",
)
@click.option("--y", required=True, help="Column name for y-axis")
@click.option(
    "--plot-type",
    type=click.Choice(["line", "scatter"]),
    default="scatter",
    help="Type of plot to create (default: scatter)",
)
@dimensional_plotting_cli(skip_fields={"x", "y"})
def main(
    dataset_path: str,
    x: str,
    y: str,
    plot_type: str,
    **kwargs: Any,
) -> None:
    df, plot_config = execute_cli_workflow(
        kwargs,
        CLIWorkflowConfig(
            data_loader=lambda _: load_dataset(dataset_path),
            allowed_unused={"save_dir", "pause"},
        ),
    )
    with FigureManager(plot_config) as fm:
        fm.plot_faceted(df, plot_type)
    show_or_save_plot(
        fm.fig,
        kwargs["save_dir"],
        kwargs["pause"],
        f"dr_plotter_{Path(dataset_path).stem}",
    )


if __name__ == "__main__":
    main()
