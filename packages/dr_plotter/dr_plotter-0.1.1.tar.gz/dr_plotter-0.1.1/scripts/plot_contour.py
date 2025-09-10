#!/usr/bin/env python3

from typing import Any

import click

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting import matrix_data
from dr_plotter.scripting.cli_framework import dimensional_plotting_cli
from dr_plotter.scripting.utils import show_or_save_plot


@click.command()
@click.option(
    "--n-components",
    type=int,
    default=2,
    help="Number of Gaussian components for mixture",
)
@click.option(
    "--n-samples",
    type=int,
    default=300,
    help="Total number of data points",
)
@click.option(
    "--density-levels",
    type=int,
    default=10,
    help="Number of contour levels to display",
)
@click.option(
    "--colormap",
    type=click.Choice(["viridis", "plasma", "coolwarm", "Blues", "hot"]),
    default="viridis",
    help="Colormap for contour visualization",
)
@click.option("--seed", type=int, default=801, help="Random seed for reproducible data")
@dimensional_plotting_cli()
def main(
    n_components: int,
    n_samples: int,
    density_levels: int,
    colormap: str,
    seed: int,
    **kwargs: Any,
) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 1, "cols": 2, "figsize": (15, 6)})
    ) as fm:
        fm.fig.suptitle("Contour Plot Showcase: Density Visualization", fontsize=16)

        # Basic contour plot - 2 component mixture
        mixture_data = matrix_data(
            pattern_type="contour",
            rows=n_samples,
            cols=2,  # Always 2D for contour (x, y)
            seed=seed,
        )
        fm.plot(
            *["contour", 0, 0, mixture_data],
            x="x",
            y="y",
            title="2-Component GMM",
            levels=density_levels,
            cmap=colormap,
        )

        # More complex mixture with different parameters
        complex_mixture = matrix_data(
            pattern_type="contour",
            rows=n_samples * 2,  # More dense sampling
            cols=2,
            seed=seed + 1,
        )
        fm.plot(
            *["contour", 0, 1, complex_mixture],
            x="x",
            y="y",
            title="3-Component GMM",
            levels=density_levels + 5,
            cmap=colormap,
        )

    show_or_save_plot(
        fm.fig,
        kwargs.get("save_dir"),
        kwargs.get("pause", 5),
        "contour_plot_showcase",
    )
    return fm.fig


if __name__ == "__main__":
    main()
