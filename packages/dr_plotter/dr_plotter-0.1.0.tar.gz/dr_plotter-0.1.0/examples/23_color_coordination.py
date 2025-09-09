"""
Example 8: Color Coordination - Cross-subplot consistency.
Demonstrates consistent colors across multiple subplots using FigureManager.
"""

from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot


@inspect_plot_properties()
@verify_plot(expected_legends=4)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 2, "cols": 2, "figsize": (15, 12)})
    ) as fm:
        fm.fig.suptitle(
            "Color Coordination: Consistent Colors Across Subplots", fontsize=16
        )

        # Use the same grouped data across all plots
        grouped_data = ExampleData.time_series_grouped()

        # All plots use the same hue variable, so colors should be consistent
        fm.plot(
            "line",
            0,
            0,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            title="Line Plot",
        )

        fm.plot(
            "scatter",
            0,
            1,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            title="Scatter Plot",
        )

        # For bar/violin plots, we need categorical data to show proper grouping
        # Create categorical data where each group appears in multiple categories
        categorical_data = ExampleData.grouped_categories(n_groups=3)

        # IMPORTANT: Rename groups to match time series data for color coordination
        # Change "Group_1", "Group_2", "Group_3" to "Group_A", "Group_B", "Group_C"
        group_mapping = {
            "Group_1": "Group_A",
            "Group_2": "Group_B",
            "Group_3": "Group_C",
        }
        categorical_data["group"] = categorical_data["group"].map(group_mapping)

        # Grouped bar plot - shows multiple groups per category
        fm.plot(
            "bar",
            1,
            0,
            categorical_data,
            x="category",
            y="value",
            hue_by="group",
            title="Grouped Bar Plot",
        )

        # Grouped violin plot - shows multiple groups per category
        fm.plot(
            "violin",
            1,
            1,
            categorical_data,
            x="category",
            y="value",
            hue_by="group",
            title="Grouped Violin Plot",
        )

    show_or_save_plot(fm.fig, args, "08_color_coordination")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Color Coordination Example")
    args = parser.parse_args()
    main(args)
