from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot


@inspect_plot_properties()
@verify_plot(expected_legends=2)
def main(args: Any) -> Any:
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

        # Simple violin plot
        simple_data = ExampleData.categorical_data()
        fm.plot(
            "violin",
            0,
            0,
            simple_data,
            x="category",
            y="value",
            title="Simple Violin Plot",
        )

        # Grouped violin plot
        grouped_data = ExampleData.grouped_categories()
        fm.plot(
            "violin",
            0,
            1,
            grouped_data,
            x="category",
            y="value",
            hue_by="group",
            title="Grouped Violin Plot",
        )

    show_or_save_plot(fm.fig, args, "12_violin_showcase")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Violin Plot Showcase")
    args = parser.parse_args()
    main(args)
