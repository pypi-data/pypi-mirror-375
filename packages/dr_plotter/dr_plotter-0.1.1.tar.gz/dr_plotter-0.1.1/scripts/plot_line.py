#!/usr/bin/env python3

from typing import Any

import click

from dr_plotter.configs import PlotConfig
from dr_plotter.consts import METRIC_COL_NAME
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting import experimental_data
from dr_plotter.scripting.cli_framework import (
    dimensional_plotting_cli,
)
from dr_plotter.scripting.utils import show_or_save_plot


@click.command()
@click.option(
    "--data-type",
    type=click.Choice(["time_series", "ml_training", "ab_test"]),
    default="time_series",
    help="Type of line data to generate",
)
@click.option("--groups", type=int, default=4, help="Number of line groups")
@click.option("--time-points", type=int, default=40, help="Number of time points")
@click.option("--seed", type=int, default=301, help="Random seed for reproducible data")
@dimensional_plotting_cli()
def main(
    data_type: str, groups: int, time_points: int, seed: int, **kwargs: Any
) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 2, "cols": 2, "figsize": (15, 12)})
    ) as fm:
        fm.fig.suptitle("Line Plot Showcase: All Visual Encoding Options", fontsize=16)

        if data_type == "time_series":
            basic_data = experimental_data(
                pattern_type="time_series",
                groups=["Single"],
                time_points=time_points,
                seed=seed,
            )
            fm.plot(
                *["line", 0, 0, basic_data],
                x="time_point",
                y="value",
                title="Basic Line Plot",
            )

            grouped_data = experimental_data(
                pattern_type="time_series",
                groups=[f"Group_{chr(65 + i)}" for i in range(groups)],
                time_points=time_points,
                seed=seed + 1,
            )
            fm.plot(
                *["line", 0, 1, grouped_data],
                x="time_point",
                y="value",
                hue_by="group",
                title="Multi-Series (hue)",
            )

            fm.plot(
                *["line", 1, 0, grouped_data],
                x="time_point",
                y="value",
                hue_by="group",
                style_by="group",
                title="Color + Line Style",
            )

        elif data_type == "ml_training":
            ml_data = experimental_data(
                pattern_type="ml_training", time_points=time_points, seed=seed
            )

            basic_loss = ml_data[ml_data["metric_name"] == "loss"].copy()
            fm.plot(
                *["line", 0, 0, basic_loss],
                x="time_point",
                y="value",
                title="Basic Training Loss",
            )

            fm.plot(
                *["line", 0, 1, basic_loss],
                x="time_point",
                y="value",
                hue_by="group",
                title="Multi-LR Training Loss",
            )

            fm.plot(
                *["line", 1, 0, basic_loss],
                x="time_point",
                y="value",
                hue_by="group",
                style_by="group",
                title="Color + Line Style",
            )

        elif data_type == "ab_test":
            ab_data = experimental_data(
                pattern_type="ab_test",
                experiments=["Exp_A", "Exp_B"],
                conditions=["Control", "Treatment"],
                time_points=time_points,
                seed=seed,
            )

            single_exp = ab_data[ab_data["experiment"] == "Exp_A"].copy()
            fm.plot(
                *["line", 0, 0, single_exp],
                x="time_point",
                y="value",
                title="Single Experiment",
            )

            fm.plot(
                *["line", 0, 1, single_exp],
                x="time_point",
                y="value",
                hue_by="condition",
                title="Control vs Treatment",
            )

            fm.plot(
                *["line", 1, 0, ab_data],
                x="time_point",
                y="value",
                hue_by="condition",
                style_by="experiment",
                title="Full A/B Test Results",
            )

        if data_type in ["time_series", "ml_training"]:
            if data_type == "time_series":
                multi_metric_data = experimental_data(
                    pattern_type="ml_training", time_points=time_points, seed=seed + 2
                )
            else:
                multi_metric_data = ml_data

            fm.plot(
                *["line", 1, 1, multi_metric_data],
                x="time_point",
                y=["train_loss", "val_loss"],
                hue_by=METRIC_COL_NAME,
                style_by="learning_rate",
                title="Multi-Metrics (METRICS)",
            )
        else:
            fm.plot(
                *["line", 1, 1, ab_data],
                x="time_point",
                y="value",
                hue_by="experiment",
                style_by="condition",
                title="Experiments + Conditions",
            )

    show_or_save_plot(
        fm.fig, kwargs.get("save_dir"), kwargs.get("pause", 5), "line_plot_showcase"
    )
    return fm.fig


if __name__ == "__main__":
    main()
