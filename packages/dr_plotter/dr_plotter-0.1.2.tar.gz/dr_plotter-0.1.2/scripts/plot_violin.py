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
    type=click.Choice(["categorical", "distribution"]),
    default="categorical",
    help="Type of violin data to generate",
)
@click.option(
    "--categories",
    type=int,
    default=4,
    help="Number of categories for categorical data",
)
@click.option("--groups", type=int, default=3, help="Number of groups")
@click.option("--n-samples", type=int, default=120, help="Total number of data points")
@click.option("--seed", type=int, default=401, help="Random seed for reproducible data")
@dimensional_plotting_cli()
def main(
    data_type: str,
    categories: int,
    groups: int,
    n_samples: int,
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
        fm.fig.suptitle("Violin Plot Showcase: Distribution Shapes", fontsize=16)

        if data_type == "categorical":
            simple_data = experimental_data(
                pattern_type="categorical",
                categories=[f"Cat_{chr(65 + i)}" for i in range(categories)],
                groups=["Single"],
                n_samples=n_samples,
                seed=seed,
            )
            fm.plot(
                *["violin", 0, 0, simple_data],
                x="category",
                y="value",
                title="Simple Violin Plot",
            )

            grouped_data = experimental_data(
                pattern_type="categorical",
                categories=[f"Cat_{chr(65 + i)}" for i in range(min(categories, 3))],
                groups=[f"Group_{chr(65 + i)}" for i in range(groups)],
                n_samples=n_samples,
                seed=seed + 1,
            )
            fm.plot(
                *["violin", 0, 1, grouped_data],
                x="category",
                y="value",
                hue_by="group",
                title="Grouped Violin Plot",
            )

        elif data_type == "distribution":
            dist_data = experimental_data(
                pattern_type="distribution",
                groups=["Normal", "Gamma", "Bimodal"],
                n_samples=n_samples,
                seed=seed,
            )
            fm.plot(
                *["violin", 0, 0, dist_data],
                x="category",
                y="value",
                title="Distribution Shapes",
            )

            multi_dist_data = experimental_data(
                pattern_type="distribution",
                groups=[
                    "Normal",
                    "Gamma",
                    "Bimodal",
                    "Uniform" if groups > 3 else "Normal",  # noqa: PLR2004
                ][: min(groups, 4)],
                n_samples=n_samples,
                seed=seed + 2,
            )

            multi_dist_data["hue_group"] = (multi_dist_data.index % 2).map(
                {0: "A", 1: "B"}
            )

            fm.plot(
                *["violin", 0, 1, multi_dist_data],
                x="category",
                y="value",
                hue_by="hue_group",
                title="Multi-Group Distributions",
            )

    show_or_save_plot(
        fm.fig,
        kwargs.get("save_dir"),
        kwargs.get("pause", 5),
        "violin_plot_showcase",
    )
    return fm.fig


if __name__ == "__main__":
    main()
