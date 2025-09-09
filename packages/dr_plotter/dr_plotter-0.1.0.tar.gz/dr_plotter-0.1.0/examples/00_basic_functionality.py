from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

EXPECTED_CHANNELS = {
    (0, 0): [],  # No encoding - basic scatter
    (0, 1): [],  # No encoding - basic line
    (1, 0): [],  # No encoding - basic bar
    (1, 1): [],  # No encoding - basic histogram
}


@inspect_plot_properties()
@verify_plot(expected_legends=0, expected_channels=EXPECTED_CHANNELS)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(
            layout={
                "rows": 2,
                "cols": 2,
                "figsize": (12, 10),
                "x_labels": [[None, None], ["Category", "Values"]],
                "y_labels": [["Y Coordinate", "Performance"], ["Average Value", None]],
            }
        )
    ) as fm:
        fm.fig.suptitle("Example 1: Basic Functionality - Core Plot Types", fontsize=16)

        # Scatter Plot (0,0)
        scatter_data = ExampleData.simple_scatter(n=80, seed=101)
        assert "x" in scatter_data.columns
        assert "y" in scatter_data.columns

        fm.plot(
            "scatter",
            0,
            0,
            scatter_data,
            x="x",
            y="y",  # REQUIRED: data mapping
            s=50,  # DEFAULT: marker size (theme default)
            alpha=0.8,  # CUSTOM: transparency override
            title="Basic Scatter Plot",  # STYLING: plot identification
        )

        # Line Plot (0,1)
        line_data = ExampleData.time_series(periods=50, seed=102)
        assert "time" in line_data.columns
        assert "value" in line_data.columns

        fm.plot(
            "line",
            0,
            1,
            line_data,
            x="time",
            y="value",  # REQUIRED: data mapping
            linewidth=2,  # DEFAULT: line width (theme default)
            alpha=0.9,  # CUSTOM: transparency override
            title="Basic Time Series",  # STYLING: plot identification
        )

        # Bar Plot (1,0)
        bar_data = ExampleData.categorical_data(
            n_categories=4, n_per_category=15, seed=103
        )
        bar_summary = bar_data.groupby("category")["value"].mean().reset_index()
        assert "category" in bar_summary.columns
        assert "value" in bar_summary.columns

        fm.plot(
            "bar",
            1,
            0,
            bar_summary,
            x="category",
            y="value",  # REQUIRED: data mapping
            width=0.8,  # DEFAULT: bar width (theme default)
            alpha=0.9,  # CUSTOM: transparency override
            title="Basic Bar Chart",  # STYLING: plot identification
        )

        # Histogram (1,1)
        hist_data = ExampleData.distribution_data(n_samples=300, seed=104)
        assert "values" in hist_data.columns

        fm.plot(
            "histogram",
            1,
            1,
            hist_data,
            x="values",  # REQUIRED: data mapping
            bins=20,  # DEFAULT: bin count (theme default)
            alpha=0.7,  # CUSTOM: transparency override
            title="Basic Histogram",  # STYLING: plot identification
        )

    show_or_save_plot(fm.fig, args, "01_basic_functionality")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Basic Functionality Example")
    args = parser.parse_args()
    main(args)
