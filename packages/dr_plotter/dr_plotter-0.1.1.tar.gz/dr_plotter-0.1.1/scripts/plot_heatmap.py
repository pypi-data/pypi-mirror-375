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
    "--pattern-type",
    type=click.Choice(["heatmap", "correlation", "contour"]),
    default="heatmap",
    help="Type of matrix pattern to generate",
)
@click.option("--matrix-rows", type=int, default=6, help="Number of rows in matrix")
@click.option("--matrix-cols", type=int, default=8, help="Number of columns in matrix")
@click.option(
    "--correlation-strength",
    type=float,
    default=0.3,
    help="Correlation strength for correlation pattern",
)
@click.option(
    "--colormap",
    type=click.Choice(["viridis", "plasma", "inferno", "magma", "coolwarm", "RdBu"]),
    default="viridis",
    help="Colormap for heatmap visualization",
)
@click.option("--seed", type=int, default=701, help="Random seed for reproducible data")
@dimensional_plotting_cli()
def main(
    pattern_type: str,
    matrix_rows: int,
    matrix_cols: int,
    correlation_strength: float,
    colormap: str,
    seed: int,
    **kwargs: Any,
) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 1, "cols": 2, "figsize": (15, 6)})
    ) as fm:
        fm.fig.suptitle("Heatmap Showcase: Matrix Visualization", fontsize=16)

        if pattern_type == "heatmap":
            # Basic heatmap
            heatmap_data = matrix_data(
                pattern_type="heatmap",
                rows=matrix_rows,
                cols=matrix_cols,
                correlation_strength=correlation_strength,
                seed=seed,
            )
            fm.plot(
                *["heatmap", 0, 0, heatmap_data],
                x="column",
                y="row",
                values="value",
                title="Basic Heatmap",
            )

            # Custom colormap heatmap
            fm.plot(
                *["heatmap", 0, 1, heatmap_data],
                x="column",
                y="row",
                values="value",
                title="Custom Colormap",
                cmap=colormap,
            )

        elif pattern_type == "correlation":
            # Correlation matrix
            corr_data = matrix_data(
                pattern_type="correlation",
                rows=min(matrix_rows, matrix_cols),  # Square matrix for correlation
                cols=min(matrix_rows, matrix_cols),
                correlation_strength=correlation_strength,
                seed=seed,
            )
            fm.plot(
                *["heatmap", 0, 0, corr_data],
                x="column",
                y="row",
                values="value",
                title="Correlation Matrix",
                cmap="RdBu",
            )

            # Different correlation strength
            strong_corr_data = matrix_data(
                pattern_type="correlation",
                rows=min(matrix_rows, matrix_cols),
                cols=min(matrix_rows, matrix_cols),
                correlation_strength=0.8,
                seed=seed + 1,
            )
            fm.plot(
                *["heatmap", 0, 1, strong_corr_data],
                x="column",
                y="row",
                values="value",
                title="Strong Correlation",
                cmap="RdBu",
            )

        elif pattern_type == "contour":
            # Contour/density data as heatmap
            contour_data = matrix_data(
                pattern_type="contour",
                rows=matrix_rows * matrix_cols // 2,
                cols=2,
                seed=seed,
            )

            # Create a grid for heatmap visualization
            import pandas as pd

            # Bin the continuous x,y data into a grid
            x_bins = pd.cut(
                contour_data["x"],
                bins=matrix_cols,
                labels=[f"Col_{i + 1}" for i in range(matrix_cols)],
            )
            y_bins = pd.cut(
                contour_data["y"],
                bins=matrix_rows,
                labels=[f"Row_{i + 1}" for i in range(matrix_rows)],
            )

            contour_data["x_bin"] = x_bins
            contour_data["y_bin"] = y_bins

            # Aggregate into heatmap format
            grid_data = (
                contour_data.groupby(["y_bin", "x_bin"])
                .size()
                .reset_index(name="value")
            )
            grid_data = grid_data.rename(columns={"x_bin": "column", "y_bin": "row"})

            fm.plot(
                *["heatmap", 0, 0, grid_data],
                x="column",
                y="row",
                values="value",
                title="Density Heatmap",
                cmap="plasma",
            )

            # Different density pattern
            dense_contour_data = matrix_data(
                pattern_type="contour",
                rows=matrix_rows * matrix_cols,
                cols=2,
                seed=seed + 2,
            )

            x_bins2 = pd.cut(
                dense_contour_data["x"],
                bins=matrix_cols,
                labels=[f"Col_{i + 1}" for i in range(matrix_cols)],
            )
            y_bins2 = pd.cut(
                dense_contour_data["y"],
                bins=matrix_rows,
                labels=[f"Row_{i + 1}" for i in range(matrix_rows)],
            )

            dense_contour_data["x_bin"] = x_bins2
            dense_contour_data["y_bin"] = y_bins2

            dense_grid_data = (
                dense_contour_data.groupby(["y_bin", "x_bin"])
                .size()
                .reset_index(name="value")
            )
            dense_grid_data = dense_grid_data.rename(
                columns={"x_bin": "column", "y_bin": "row"}
            )

            fm.plot(
                *["heatmap", 0, 1, dense_grid_data],
                x="column",
                y="row",
                values="value",
                title="High Density",
                cmap="plasma",
            )

    show_or_save_plot(
        fm.fig,
        kwargs.get("save_dir"),
        kwargs.get("pause", 5),
        "heatmap_plot_showcase",
    )
    return fm.fig


if __name__ == "__main__":
    main()
