from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

EXPECTED_CHANNELS = {
    (0, 0): ["hue"],
    (0, 1): ["hue"],
    (1, 0): ["hue"],
    (1, 1): ["hue"],
}


@inspect_plot_properties()
@verify_plot(
    expected_legends=4,
    expected_channels=EXPECTED_CHANNELS,
    verify_legend_consistency=True,
    expected_legend_entries={
        (0, 0): {"hue": 2},
        (0, 1): {"hue": 2},
        (1, 0): {"hue": 4},
        (1, 1): {"hue": 4},
    },
)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(
            layout={
                "rows": 2,
                "cols": 2,
                "figsize": (15, 12),
                "x_labels": [[None, None], ["Time (units)", "Category"]],
                "y_labels": [["Performance", "Value"], ["Performance", None]],
            }
        )
    ) as fm:
        fm.fig.suptitle("Grouped Plotting: Side-by-Side Comparisons", fontsize=16)

        # Simple grouping: 2 groups for clear comparison
        simple_grouped = ExampleData.grouped_categories(n_groups=2)

        # Simple grouped bar charts
        fm.plot(
            "bar",
            0,
            0,
            simple_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="2-Group Bar Chart",
        )

        # Simple grouped violin plots
        fm.plot(
            "violin",
            0,
            1,
            simple_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="2-Group Violin Plot",
        )

        # Complex grouping: 4 groups for more complex comparison
        complex_grouped = ExampleData.grouped_categories(n_groups=4)
        fm.plot(
            "bar",
            1,
            0,
            complex_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="4-Group Bar Chart",
        )

        # Complex grouped violin plots
        fm.plot(
            "violin",
            1,
            1,
            complex_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="4-Group Violin Plot",
        )

    show_or_save_plot(fm.fig, args, "07_grouped_plotting")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Grouped Plotting Example")
    args = parser.parse_args()
    main(args)
