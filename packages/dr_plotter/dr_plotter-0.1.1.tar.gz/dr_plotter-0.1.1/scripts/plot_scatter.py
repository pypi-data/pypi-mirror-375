#!/usr/bin/env python3

from typing import Any

import click

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting import experimental_data
from dr_plotter.scripting.cli_framework import dimensional_plotting_cli
from dr_plotter.scripting.utils import show_or_save_plot


@click.command()
@click.option(
    "--data-type",
    type=click.Choice(["multi_dimensional", "time_series", "categorical"]),
    default="multi_dimensional",
    help="Type of scatter data to generate",
)
@click.option("--experiments", type=int, default=2, help="Number of experiments")
@click.option("--conditions", type=int, default=2, help="Number of conditions")
@click.option("--categories", type=int, default=3, help="Number of categories")
@click.option("--n-samples", type=int, default=120, help="Total number of data points")
@click.option("--seed", type=int, default=501, help="Random seed for reproducible data")
@dimensional_plotting_cli()
def main(
    data_type: str,
    experiments: int,
    conditions: int,
    categories: int,
    n_samples: int,
    seed: int,
    **kwargs: Any,
) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 2, "cols": 2, "figsize": (15, 12)})
    ) as fm:
        fm.fig.suptitle(
            "Scatter Plot Showcase: All Visual Encoding Options", fontsize=16
        )

        if data_type == "multi_dimensional":
            # Basic scatter using multi_dimensional data
            basic_data = experimental_data(
                pattern_type="multi_dimensional",
                experiments=[f"Exp_{chr(65 + i)}" for i in range(1)],
                conditions=["Single"],
                categories=[f"Cat_{chr(65 + i)}" for i in range(1)],
                n_samples=n_samples,
                seed=seed,
            )
            fm.plot(
                *["scatter", 0, 0, basic_data],
                x="x_continuous",
                y="y_continuous",
                title="Basic Scatter",
            )

            # Color encoding (hue) - using experiments
            grouped_data = experimental_data(
                pattern_type="multi_dimensional",
                experiments=[f"Exp_{chr(65 + i)}" for i in range(experiments)],
                conditions=["Control"],
                categories=[f"Cat_{chr(65 + i)}" for i in range(1)],
                n_samples=n_samples,
                seed=seed + 1,
            )
            fm.plot(
                *["scatter", 0, 1, grouped_data],
                x="x_continuous",
                y="y_continuous",
                hue_by="experiment",
                title="Color Encoding (hue)",
            )

            # Another hue encoding with conditions
            condition_data = experimental_data(
                pattern_type="multi_dimensional",
                experiments=[f"Exp_{chr(65 + i)}" for i in range(experiments)],
                conditions=[f"Cond_{chr(65 + i)}" for i in range(conditions)],
                categories=[f"Cat_{chr(65 + i)}" for i in range(1)],
                n_samples=n_samples,
                seed=seed + 2,
            )
            fm.plot(
                *["scatter", 1, 0, condition_data],
                x="x_continuous",
                y="y_continuous",
                hue_by="experiment",
                title="Color Encoding",
            )

            # Marker encoding - color by condition, marker by algorithm
            complex_data = experimental_data(
                pattern_type="multi_dimensional",
                experiments=[f"Exp_{chr(65 + i)}" for i in range(experiments)],
                conditions=["Control", "Treatment"],
                categories=[f"Cat_{chr(65 + i)}" for i in range(categories)],
                n_samples=n_samples,
                seed=seed + 3,
            )
            fm.plot(
                *["scatter", 1, 1, complex_data],
                x="x_continuous",
                y="y_continuous",
                hue_by="condition",
                marker_by="algorithm",
                title="Color + Marker Encoding",
            )

        elif data_type == "time_series":
            # Time-based scatter plots
            time_data = experimental_data(
                pattern_type="time_series",
                groups=["Single"],
                time_points=50,
                seed=seed,
            )
            fm.plot(
                *["scatter", 0, 0, time_data],
                x="time_point",
                y="value",
                title="Time Series Scatter",
            )

            grouped_time_data = experimental_data(
                pattern_type="time_series",
                groups=[f"Group_{chr(65 + i)}" for i in range(3)],
                time_points=40,
                seed=seed + 1,
            )
            fm.plot(
                *["scatter", 0, 1, grouped_time_data],
                x="time_point",
                y="value",
                hue_by="group",
                title="Grouped Time Series",
            )

            fm.plot(
                *["scatter", 1, 0, grouped_time_data],
                x="x_continuous",
                y="y_continuous",
                hue_by="group",
                title="Continuous Variables",
            )

            fm.plot(
                *["scatter", 1, 1, grouped_time_data],
                x="time_point",
                y="value",
                hue_by="group",
                marker_by="category",
                title="Time + Category Encoding",
            )

        elif data_type == "categorical":
            # Categorical-based scatter plots
            cat_data = experimental_data(
                pattern_type="categorical",
                categories=[f"Cat_{chr(65 + i)}" for i in range(categories)],
                groups=["Single"],
                n_samples=n_samples,
                seed=seed,
            )
            fm.plot(
                *["scatter", 0, 0, cat_data],
                x="x_continuous",
                y="y_continuous",
                title="Basic Continuous Scatter",
            )

            grouped_cat_data = experimental_data(
                pattern_type="categorical",
                categories=[f"Cat_{chr(65 + i)}" for i in range(categories)],
                groups=[f"Group_{chr(65 + i)}" for i in range(3)],
                n_samples=n_samples,
                seed=seed + 1,
            )
            fm.plot(
                *["scatter", 0, 1, grouped_cat_data],
                x="x_continuous",
                y="value",
                hue_by="category",
                title="Category Encoding",
            )

            fm.plot(
                *["scatter", 1, 0, grouped_cat_data],
                x="x_continuous",
                y="y_continuous",
                hue_by="group",
                title="Group Encoding",
            )

            fm.plot(
                *["scatter", 1, 1, grouped_cat_data],
                x="x_continuous",
                y="value",
                hue_by="category",
                marker_by="group",
                title="Category + Group Encoding",
            )

    show_or_save_plot(
        fm.fig,
        kwargs.get("save_dir"),
        kwargs.get("pause", 5),
        "scatter_plot_showcase",
    )
    return fm.fig


if __name__ == "__main__":
    main()
