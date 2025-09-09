"""
Example 5: Multi-Series Plotting - Visual encoding channels.
Demonstrates all visual encoding options: hue, style, size, marker, alpha.
"""

from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

EXPECTED_CHANNELS = {
    (0, 0): ["hue", "marker"],
    (0, 1): ["hue"],
    (1, 1): ["hue", "alpha"],
}


@inspect_plot_properties()
@verify_plot(
    expected_legends=4,
    expected_channels=EXPECTED_CHANNELS,
    verify_legend_consistency=True,
    expected_legend_entries={
        (0, 0): {"hue": 3, "marker": 2},
        (0, 1): {"hue": 2},
        (1, 1): {"hue": 3, "alpha": 2},
    },
)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 2, "cols": 2, "figsize": (15, 12)})
    ) as fm:
        fm.fig.suptitle("Multi-Series: All Visual Encoding Channels", fontsize=16)

        complex_data = ExampleData.complex_encoding_data()

        fm.plot(
            "scatter",
            0,
            0,
            complex_data,
            x="x",
            y="y",
            hue_by="experiment",
            marker_by="condition",
            title="Scatter: hue + marker",
        )

        fm.plot(
            "scatter",
            0,
            1,
            complex_data,
            x="x",
            y="y",
            hue_by="condition",
            title="Scatter: hue only",
        )

        grouped_ts = ExampleData.time_series_grouped(periods=30, groups=4)

        fm.plot(
            "line",
            1,
            0,
            grouped_ts,
            x="time",
            y="value",
            hue_by="group",
            style_by="group",
            title="Line: hue + style",
        )

        fm.plot(
            "scatter",
            1,
            1,
            complex_data,
            x="x",
            y="y",
            hue_by="experiment",
            alpha_by="algorithm",
            title="Scatter: hue + alpha",
        )

    show_or_save_plot(fm.fig, args, "05_multi_series_plotting")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Multi-Series Plotting Example")
    args = parser.parse_args()
    main(args)
