from typing import Any

import numpy as np
from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot


@inspect_plot_properties()
@verify_plot(expected_legends=2)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 1, "cols": 2, "figsize": (15, 6)})
    ) as fm:
        fm.fig.suptitle("Layering: Combining Multiple Plot Types", fontsize=16)

        scatter_data = ExampleData.simple_scatter()
        fm.plot(
            "scatter",
            0,
            0,
            scatter_data,
            x="x",
            y="y",
            alpha=0.6,
            title="Scatter + Manual Line Overlay",
        )

        sorted_data = scatter_data.sort_values("x")
        fm.axes[0].plot(
            sorted_data["x"],
            sorted_data["y"],
            color="red",
            linewidth=2,
            label="Trend line",
        )
        fm.axes[0].legend()

        dist_data = ExampleData.distribution_data()
        fm.plot(
            "histogram",
            0,
            1,
            dist_data,
            x="values",
            alpha=0.7,
            density=True,
            bins=30,
            title="Histogram + Theoretical Curve",
        )

        x_theory = np.linspace(
            dist_data["values"].min(), dist_data["values"].max(), 100
        )
        y_theory = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x_theory**2)
        fm.axes[1].plot(x_theory, y_theory, "r-", linewidth=2, label="Standard normal")
        fm.axes[1].legend()

    show_or_save_plot(fm.fig, args, "15_layering_plots")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Layering Example")
    args = parser.parse_args()
    main(args)
