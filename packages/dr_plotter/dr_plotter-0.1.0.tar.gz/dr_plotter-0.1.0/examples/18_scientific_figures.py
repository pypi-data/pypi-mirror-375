from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot


@inspect_plot_properties()
@verify_plot(expected_legends=2)
def main(args: Any) -> Any:
    # Create publication-style figure
    with FigureManager(
        PlotConfig(layout={"rows": 2, "cols": 3, "figsize": (18, 12)})
    ) as fm:
        fm.fig.suptitle(
            "Scientific Data Analysis: Multi-Panel Figure", fontsize=16, y=0.95
        )

        # Panel A: Time series data
        ts_data = ExampleData.time_series_grouped(periods=50, groups=3)
        fm.plot(
            "line",
            0,
            0,
            ts_data,
            x="time",
            y="value",
            hue_by="group",
            title="A) Temporal Dynamics",
            xlabel="Time (hours)",
            ylabel="Signal Intensity",
        )

        # Panel B: Distribution comparison
        dist_data = ExampleData.distribution_data(distributions=3)
        fm.plot(
            "violin",
            0,
            1,
            dist_data,
            x="distribution",
            y="value",
            title="B) Response Distributions",
            xlabel="Treatment Group",
            ylabel="Response",
        )

        # Panel C: Correlation analysis
        corr_data = ExampleData.simple_scatter(n=200)
        fm.plot(
            "scatter",
            0,
            2,
            corr_data,
            x="x",
            y="y",
            title="C) Variable Correlation",
            xlabel="Predictor X",
            ylabel="Response Y",
        )

        # Panel D: Categorical analysis
        cat_data = ExampleData.grouped_categories()
        cat_summary = (
            cat_data.groupby(["category", "group"])["value"].mean().reset_index()
        )
        fm.plot(
            "bar",
            1,
            0,
            cat_summary,
            x="category",
            y="value",
            hue_by="group",
            title="D) Treatment Effects",
            xlabel="Condition",
            ylabel="Mean Response",
        )

        # Panel E: Heatmap of relationships
        heatmap_data = ExampleData.heatmap_data(rows=6, cols=6)
        fm.plot(
            "heatmap",
            1,
            1,
            heatmap_data,
            x="column",
            y="row",
            values="value",
            title="E) Correlation Matrix",
            cmap="RdBu_r",
        )

        # Panel F: Ranking over time
        ranking_data = ExampleData.ranking_data(time_points=10, categories=4)
        fm.plot(
            "bump",
            1,
            2,
            ranking_data,
            time_col="time",
            category_col="category",
            value_col="score",
            title="F) Performance Rankings",
        )

        # Adjust layout for better appearance
        # Skip tight_layout due to colorbar compatibility issue
        fm.fig.subplots_adjust(
            top=0.92, bottom=0.08, left=0.08, right=0.95, hspace=0.3, wspace=0.3
        )

    show_or_save_plot(fm.fig, args, "18_scientific_figures")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Scientific Figures Example")
    args = parser.parse_args()
    main(args)
