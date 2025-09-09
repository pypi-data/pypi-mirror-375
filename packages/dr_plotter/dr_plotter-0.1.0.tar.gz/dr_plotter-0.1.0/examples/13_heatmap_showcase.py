from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot


@inspect_plot_properties()
@verify_plot(expected_legends=0)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 1, "cols": 2, "figsize": (15, 6)})
    ) as fm:
        fm.fig.suptitle("Heatmap Showcase: Matrix Visualization", fontsize=16)

        # Basic heatmap
        heatmap_data = ExampleData.heatmap_data()
        fm.plot(
            "heatmap",
            0,
            0,
            heatmap_data,
            x="column",
            y="row",
            values="value",
            title="Basic Heatmap",
        )

        # Custom colormap heatmap
        fm.plot(
            "heatmap",
            0,
            1,
            heatmap_data,
            x="column",
            y="row",
            values="value",
            title="Custom Colormap",
            cmap="viridis",
        )

    show_or_save_plot(fm.fig, args, "13_heatmap_showcase")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Heatmap Showcase")
    args = parser.parse_args()
    main(args)
