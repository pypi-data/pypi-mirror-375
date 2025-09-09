from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import LayoutConfig, PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.legend_manager import LegendConfig
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import (
    inspect_plot_properties,
    verify_figure_legends,
)

EXPECTED_CATEGORY_GROUP_COUNT = 4


@inspect_plot_properties()
@verify_figure_legends(
    expected_legend_count=1, legend_strategy="figure_below", expected_total_entries=4
)
def main(args: Any) -> Any:
    shared_data = ExampleData.get_legend_positioning_data()
    time_series_data = ExampleData.get_category_time_series()

    assert "category_group" in shared_data.columns
    assert "performance" in shared_data.columns
    assert "accuracy" in shared_data.columns
    assert len(shared_data.groupby("category_group")) == EXPECTED_CATEGORY_GROUP_COUNT

    with FigureManager(
        PlotConfig(
            layout=LayoutConfig(rows=2, cols=2, figsize=(16, 12)),
            legend=LegendConfig(
                strategy="figure",
                ncol=4,
                layout_bottom_margin=0.08,
            ),
        )
    ) as fm:
        fm.fig.suptitle(
            "Example 10: Legend Positioning + Management - Shared Figure Legend",
            fontsize=16,
        )

        fm.plot(
            "scatter",
            0,
            0,
            shared_data,
            x="performance",
            y="accuracy",
            hue_by="category_group",
            s=60,
            alpha=0.8,
            title="Scatter: Contributing to Shared Legend",
        )

        fm.plot(
            "line",
            0,
            1,
            time_series_data,
            x="time_point",
            y="performance",
            hue_by="category_group",
            linewidth=2,
            alpha=0.8,
            title="Line: Contributing to Shared Legend",
        )

        fm.plot(
            "scatter",
            1,
            0,
            shared_data,
            x="runtime",
            y="memory",
            hue_by="category_group",
            s=60,
            alpha=0.8,
            title="Scatter Alt: Contributing to Shared Legend",
        )

        fm.plot(
            "scatter",
            1,
            1,
            shared_data,
            x="performance",
            y="accuracy",
            hue_by="category_group",
            s=60,
            alpha=0.8,
            legend=False,
            title="No Legend: Grouping Without Legend Display",
        )

    show_or_save_plot(fm.fig, args, "10_legend_positioning")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(
        description="Legend Positioning + Management - Legend System Robustness"
    )
    args = parser.parse_args()
    main(args)
