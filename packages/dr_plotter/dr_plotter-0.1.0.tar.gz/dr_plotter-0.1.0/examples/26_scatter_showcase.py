"""
Example 9: Scatter Plot Showcase - All scatter plot features.
Demonstrates all visual encoding options for scatter plots.
"""

from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

EXPECTED_CHANNELS = {
    (0, 1): ["hue"],
    (1, 0): ["hue"],
    (1, 1): ["hue", "marker"],
}


@inspect_plot_properties()
@verify_plot(
    expected_legends=3,
    expected_channels=EXPECTED_CHANNELS,
    verify_legend_consistency=True,
    expected_legend_entries={
        (0, 1): {"hue": 3},
        (1, 0): {"hue": 3},
        (1, 1): {"hue": 2, "marker": 2},
    },
)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 2, "cols": 2, "figsize": (15, 12)})
    ) as fm:
        fm.fig.suptitle(
            "Scatter Plot Showcase: All Visual Encoding Options", fontsize=16
        )

        # Basic scatter
        basic_data = ExampleData.simple_scatter()
        fm.plot("scatter", 0, 0, basic_data, x="x", y="y", title="Basic Scatter")

        # Color encoding (hue)
        grouped_data = ExampleData.time_series_grouped(periods=30)
        fm.plot(
            "scatter",
            0,
            1,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            title="Color Encoding (hue)",
        )

        # Another hue encoding example
        complex_data = ExampleData.complex_encoding_data()
        fm.plot(
            "scatter",
            1,
            0,
            complex_data,
            x="x",
            y="y",
            hue_by="experiment",
            title="Color Encoding",
        )

        # Marker encoding
        fm.plot(
            "scatter",
            1,
            1,
            complex_data,
            x="x",
            y="y",
            hue_by="condition",
            marker_by="algorithm",
            title="Color + Marker Encoding",
        )

    show_or_save_plot(fm.fig, args, "09_scatter_showcase")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Scatter Plot Showcase")
    args = parser.parse_args()
    main(args)
