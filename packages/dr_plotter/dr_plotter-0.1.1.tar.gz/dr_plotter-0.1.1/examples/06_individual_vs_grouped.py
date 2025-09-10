from typing import Any

from dr_plotter.scripting import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

MIN_CATEGORY_GROUP_COUNT = 2

EXPECTED_CHANNELS = {
    (0, 0): [],
    (0, 1): [],
    (0, 2): [],
    (0, 3): [],
    (1, 0): ["hue"],
    (1, 1): ["hue"],
    (1, 2): ["hue"],
    (1, 3): ["hue"],
}


@inspect_plot_properties()
@verify_plot(
    expected_legends=4,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (1, 0): {"hue": 3},
        (1, 1): {"hue": 3},
        (1, 2): {"hue": 3},
        (1, 3): {"hue": 3},
    },
)
def main(args: Any) -> Any:
    shared_data = ExampleData.get_individual_vs_grouped_data()

    assert "x_continuous" in shared_data.columns
    assert "y_continuous" in shared_data.columns
    assert "x_categorical" in shared_data.columns
    assert "category_group" in shared_data.columns
    assert "time_series" in shared_data.columns
    assert len(shared_data.groupby("category_group")) >= MIN_CATEGORY_GROUP_COUNT

    aggregated_data = (
        shared_data.groupby("x_categorical")["y_continuous"].mean().reset_index()
    )

    with FigureManager(
        PlotConfig(layout={"rows": 2, "cols": 4, "figsize": (20, 10)})
    ) as fm:
        fm.fig.suptitle("Individual vs Grouped Plotting Comparison", fontsize=16)

        fm.plot(
            "scatter",
            0,
            0,
            shared_data,
            x="x_continuous",
            y="y_continuous",
            color="steelblue",
            alpha=0.7,
            s=50,
            title="Individual: Single Color, No Grouping",
        )

        fm.plot(
            "line",
            0,
            1,
            shared_data,
            x="time_series",
            y="y_continuous",
            color="darkgreen",
            linewidth=2,
            alpha=0.8,
            title="Individual: Single Line, No Grouping",
        )

        fm.plot(
            "violin",
            0,
            2,
            shared_data,
            x="x_categorical",
            y="y_continuous",
            color="purple",
            alpha=0.6,
            title="Individual: Single Color, No Grouping",
        )

        fm.plot(
            "bar",
            0,
            3,
            aggregated_data,
            x="x_categorical",
            y="y_continuous",
            color="orange",
            alpha=0.8,
            title="Individual: Single Color, No Grouping",
        )

        fm.plot(
            "scatter",
            1,
            0,
            shared_data,
            x="x_continuous",
            y="y_continuous",
            hue_by="category_group",
            alpha=0.7,
            s=50,
            title="Grouped: Hue Encoding by Category",
        )

        fm.plot(
            "line",
            1,
            1,
            shared_data,
            x="time_series",
            y="y_continuous",
            hue_by="category_group",
            linewidth=2,
            alpha=0.8,
            title="Grouped: Color and Style by Category",
        )

        fm.plot(
            "violin",
            1,
            2,
            shared_data,
            x="x_categorical",
            y="y_continuous",
            hue_by="category_group",
            alpha=0.6,
            title="Grouped: Color Encoding by Category",
        )

        fm.plot(
            "bar",
            1,
            3,
            shared_data,
            x="x_categorical",
            y="y_continuous",
            hue_by="category_group",
            alpha=0.8,
            title="Grouped: Color Encoding by Category",
        )

    show_or_save_plot(fm.fig, args, "06_individual_vs_grouped")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Individual vs Grouped Plotting Comparison")
    args = parser.parse_args()
    main(args)
