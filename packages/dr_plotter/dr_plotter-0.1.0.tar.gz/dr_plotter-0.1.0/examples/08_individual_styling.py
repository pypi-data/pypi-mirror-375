import itertools
from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot
from dr_plotter.theme import BASE_THEME, PlotStyles, Theme

EXPECTED_CHANNELS = {
    (0, 0): ["hue"],
    (0, 1): ["hue"],
    (0, 2): ["hue"],
    (1, 0): [],
    (1, 1): [],
    (1, 2): [],
}


def create_bold_theme() -> Theme:
    return Theme(
        name="bold_styling",
        parent=BASE_THEME,
        plot_styles=PlotStyles(
            alpha=1.0,
            linewidth=4,
        ),
        hue_cycle=itertools.cycle(
            ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"]
        ),
    )


def create_subtle_theme() -> Theme:
    return Theme(
        name="subtle_styling",
        parent=BASE_THEME,
        plot_styles=PlotStyles(
            alpha=0.6,
            linewidth=1,
        ),
        hue_cycle=itertools.cycle(["#95A5A6", "#BDC3C7", "#D5DBDB", "#85929E"]),
    )


def create_vibrant_theme() -> Theme:
    return Theme(
        name="vibrant_styling",
        parent=BASE_THEME,
        plot_styles=PlotStyles(
            alpha=0.9,
            linewidth=3,
        ),
        hue_cycle=itertools.cycle(
            ["#E74C3C", "#9B59B6", "#3498DB", "#1ABC9C", "#F39C12"]
        ),
    )


@inspect_plot_properties()
@verify_plot(
    expected_legends=3,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 0): {"hue": 3},
        (0, 1): {"hue": 4},
        (0, 2): {"hue": 3},
    },
)
def main(args: Any) -> Any:
    data = ExampleData.get_individual_styling_data()

    with FigureManager(
        PlotConfig(
            layout={
                "rows": 2,
                "cols": 3,
                "figsize": (18, 12),
                "x_labels": [
                    [None, None, None],
                    ["Category", "Values", "Column Index"],
                ],
                "y_labels": [
                    ["Y Coordinate", "Performance", "Value"],
                    ["Count", None, None],
                ],
            }
        )
    ) as fm:
        fm.fig.suptitle("Individual Styling: Per-Subplot Customization", fontsize=16)

        bold_theme = create_bold_theme()
        fm.plot(
            "scatter",
            0,
            0,
            data["scatter_data"],
            x="x",
            y="y",
            hue_by="category",
            theme=bold_theme,
            s=80,
            title="Scatter: Bold Theme Override",
        )

        subtle_theme = create_subtle_theme()
        fm.plot(
            "line",
            0,
            1,
            data["line_data"],
            x="time",
            y="value",
            hue_by="group",
            theme=subtle_theme,
            linewidth=3,
            title="Line: Subtle Theme Override",
        )

        vibrant_theme = create_vibrant_theme()
        fm.plot(
            "violin",
            0,
            2,
            data["violin_data"],
            x="category",
            y="value",
            hue_by="group",
            theme=vibrant_theme,
            alpha=0.8,
            title="Violin: Vibrant Theme Override",
        )

        fm.plot(
            "bar",
            1,
            0,
            data["bar_data"],
            x="category",
            y="value",
            color="#FF6B6B",
            alpha=0.9,
            edgecolor="black",
            linewidth=2,
            title="Bar: Heavy Parameter Customization",
        )

        fm.plot(
            "histogram",
            1,
            1,
            data["histogram_data"],
            x="values",
            bins=25,
            color="#4ECDC4",
            alpha=0.7,
            edgecolor="white",
            linewidth=1.5,
            title="Histogram: Parameter-Based Styling",
        )

        fm.plot(
            "heatmap",
            1,
            2,
            data["heatmap_data"],
            x="column",
            y="row",
            values="value",
            cmap="plasma",
            alpha=0.95,
            title="Heatmap: Colormap Customization",
        )

    show_or_save_plot(fm.fig, args, "08_individual_styling")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(
        description="Individual Styling Grid - Per-Subplot Customization"
    )
    args = parser.parse_args()
    main(args)
