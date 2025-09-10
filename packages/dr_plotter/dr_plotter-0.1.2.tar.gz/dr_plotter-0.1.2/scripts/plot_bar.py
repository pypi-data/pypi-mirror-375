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
    type=click.Choice(["categorical", "distribution", "multi_dimensional"]),
    default="categorical",
    help="Type of bar data to generate",
)
@click.option("--categories", type=int, default=4, help="Number of categories")
@click.option("--groups", type=int, default=3, help="Number of groups")
@click.option("--n-samples", type=int, default=120, help="Total number of data points")
@click.option(
    "--aggregate",
    type=click.Choice(["mean", "sum", "count"]),
    default="mean",
    help="Aggregation method for bar heights",
)
@click.option("--seed", type=int, default=601, help="Random seed for reproducible data")
@dimensional_plotting_cli()
def main(
    data_type: str,
    categories: int,
    groups: int,
    n_samples: int,
    aggregate: str,
    seed: int,
    **kwargs: Any,
) -> Any:
    with FigureManager(
        PlotConfig(
            layout={
                "rows": 1,
                "cols": 2,
                "figsize": (15, 6),
                "x_labels": [["Category", "Category"]],
                "y_labels": [["Value", None]],
            }
        )
    ) as fm:
        fm.fig.suptitle("Bar Plot Showcase: Single and Grouped Bars", fontsize=16)

        if data_type == "categorical":
            # Simple bar chart - aggregate categorical data
            simple_data = experimental_data(
                pattern_type="categorical",
                categories=[f"Cat_{chr(65 + i)}" for i in range(categories)],
                groups=["Single"],
                n_samples=n_samples,
                seed=seed,
            )

            # Aggregate data for bar chart
            if aggregate == "mean":
                simple_summary = (
                    simple_data.groupby("category")["value"].mean().reset_index()
                )
            elif aggregate == "sum":
                simple_summary = (
                    simple_data.groupby("category")["value"].sum().reset_index()
                )
            else:  # count
                simple_summary = (
                    simple_data.groupby("category").size().reset_index(name="value")
                )

            fm.plot(
                *["bar", 0, 0, simple_summary],
                x="category",
                y="value",
                label="Category Values",
                title="Simple Bar Chart",
            )

            # Grouped bar chart
            grouped_data = experimental_data(
                pattern_type="categorical",
                categories=[f"Cat_{chr(65 + i)}" for i in range(min(categories, 4))],
                groups=[f"Group_{chr(65 + i)}" for i in range(groups)],
                n_samples=n_samples,
                seed=seed + 1,
            )

            # Aggregate grouped data
            if aggregate == "mean":
                grouped_summary = (
                    grouped_data.groupby(["category", "group"])["value"]
                    .mean()
                    .reset_index()
                )
            elif aggregate == "sum":
                grouped_summary = (
                    grouped_data.groupby(["category", "group"])["value"]
                    .sum()
                    .reset_index()
                )
            else:  # count
                grouped_summary = (
                    grouped_data.groupby(["category", "group"])
                    .size()
                    .reset_index(name="value")
                )

            fm.plot(
                *["bar", 0, 1, grouped_summary],
                x="category",
                y="value",
                hue_by="group",
                title="Grouped Bar Chart",
            )

        elif data_type == "distribution":
            # Distribution-based bar charts
            dist_data = experimental_data(
                pattern_type="distribution",
                groups=[f"Dist_{i + 1}" for i in range(min(groups, 4))],
                n_samples=n_samples,
                seed=seed,
            )

            # Aggregate by distribution type
            if aggregate == "mean":
                dist_summary = (
                    dist_data.groupby("category")["value"].mean().reset_index()
                )
            elif aggregate == "sum":
                dist_summary = (
                    dist_data.groupby("category")["value"].sum().reset_index()
                )
            else:  # count
                dist_summary = (
                    dist_data.groupby("category").size().reset_index(name="value")
                )

            fm.plot(
                *["bar", 0, 0, dist_summary],
                x="category",
                y="value",
                label="Distribution Summary",
                title="Distribution Bar Chart",
            )

            # Grouped by distribution characteristics
            import pandas as pd

            dist_data["range_group"] = pd.cut(
                dist_data["value"], bins=3, labels=["Low", "Medium", "High"]
            )

            if aggregate == "count":
                range_summary = (
                    dist_data.groupby(["category", "range_group"])
                    .size()
                    .reset_index(name="value")
                )
            else:
                range_summary = (
                    dist_data.groupby(["category", "range_group"])["value"].mean()
                    if aggregate == "mean"
                    else dist_data.groupby(["category", "range_group"])["value"].sum()
                ).reset_index()

            fm.plot(
                *["bar", 0, 1, range_summary],
                x="category",
                y="value",
                hue_by="range_group",
                title="Range-Grouped Bar Chart",
            )

        elif data_type == "multi_dimensional":
            # Multi-dimensional bar charts
            multi_data = experimental_data(
                pattern_type="multi_dimensional",
                experiments=[f"Exp_{chr(65 + i)}" for i in range(min(categories, 3))],
                conditions=["Control", "Treatment"],
                categories=[f"Cat_{chr(65 + i)}" for i in range(min(groups, 3))],
                n_samples=n_samples,
                seed=seed,
            )

            # Aggregate by experiment
            if aggregate == "mean":
                exp_summary = (
                    multi_data.groupby("experiment")["value"].mean().reset_index()
                )
            elif aggregate == "sum":
                exp_summary = (
                    multi_data.groupby("experiment")["value"].sum().reset_index()
                )
            else:  # count
                exp_summary = (
                    multi_data.groupby("experiment").size().reset_index(name="value")
                )

            fm.plot(
                *["bar", 0, 0, exp_summary],
                x="experiment",
                y="value",
                label="Experiment Results",
                title="Experiment Bar Chart",
            )

            # Grouped by condition and experiment
            if aggregate == "mean":
                cond_summary = (
                    multi_data.groupby(["experiment", "condition"])["value"]
                    .mean()
                    .reset_index()
                )
            elif aggregate == "sum":
                cond_summary = (
                    multi_data.groupby(["experiment", "condition"])["value"]
                    .sum()
                    .reset_index()
                )
            else:  # count
                cond_summary = (
                    multi_data.groupby(["experiment", "condition"])
                    .size()
                    .reset_index(name="value")
                )

            fm.plot(
                *["bar", 0, 1, cond_summary],
                x="experiment",
                y="value",
                hue_by="condition",
                title="Condition-Grouped Bar Chart",
            )

    show_or_save_plot(
        fm.fig,
        kwargs.get("save_dir"),
        kwargs.get("pause", 5),
        "bar_plot_showcase",
    )
    return fm.fig


if __name__ == "__main__":
    main()
