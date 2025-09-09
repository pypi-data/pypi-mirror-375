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
        PlotConfig(layout={"rows": 2, "cols": 2, "figsize": (15, 12)})
    ) as fm:
        fm.fig.suptitle(
            "Matplotlib Integration: Direct Parameter Pass-Through", fontsize=16
        )

        # Scatter with matplotlib parameters
        scatter_data = ExampleData.simple_scatter()
        fm.plot(
            "scatter",
            0,
            0,
            scatter_data,
            x="x",
            y="y",
            title="Custom Scatter Styling",
            s=100,  # matplotlib: marker size
            alpha=0.6,  # matplotlib: transparency
            edgecolors="black",  # matplotlib: edge colors
            linewidths=1,
        )  # matplotlib: edge width

        # Line plot with advanced matplotlib styling
        line_data = ExampleData.time_series()
        fm.plot(
            "line",
            0,
            1,
            line_data,
            x="time",
            y="value",
            title="Advanced Line Styling",
            linewidth=3,  # matplotlib: line width
            linestyle="--",  # matplotlib: line style
            marker="o",  # matplotlib: markers
            markersize=8,  # matplotlib: marker size
            markerfacecolor="red",  # matplotlib: marker fill
            markeredgecolor="black",  # matplotlib: marker edge
            alpha=0.8,
        )  # matplotlib: transparency

        # Histogram with matplotlib parameters
        hist_data = ExampleData.distribution_data()
        fm.plot(
            "histogram",
            1,
            0,
            hist_data,
            x="values",
            title="Custom Histogram",
            bins=25,  # matplotlib: number of bins
            alpha=0.7,  # matplotlib: transparency
            color="green",  # matplotlib: color
            edgecolor="black",  # matplotlib: edge color
            linewidth=1.5,
        )  # matplotlib: edge width

        # Bar plot with matplotlib styling
        bar_data = ExampleData.categorical_data()
        bar_summary = bar_data.groupby("category")["value"].mean().reset_index()
        fm.plot(
            "bar",
            1,
            1,
            bar_summary,
            x="category",
            y="value",
            title="Custom Bar Styling",
            alpha=0.8,  # matplotlib: transparency
            color="orange",  # matplotlib: color
            edgecolor="darkred",  # matplotlib: edge color
            linewidth=2,  # matplotlib: edge width
            width=0.6,
        )  # matplotlib: bar width

    show_or_save_plot(fm.fig, args, "16_matplotlib_integration")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Matplotlib Integration Example")
    args = parser.parse_args()
    main(args)
