from typing import Any

from dr_plotter.scripting import ExampleData

from dr_plotter.configs import (
    PlotConfig,
    PositioningConfig,
)
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties


@inspect_plot_properties()
def main(args: Any) -> Any:
    line_data = ExampleData.time_series(periods=50, seed=102)
    assert "time" in line_data.columns
    assert "value" in line_data.columns

    positioning_config = PositioningConfig(
        default_margin_bottom=0.15,
        default_margin_top=0.95,
        default_margin_left=0.0,
        default_margin_right=1.0,
        legend_y_offset_factor=0.08,
        legend_spacing_base=0.35,
        legend_alignment_center=0.5,
        two_legend_positions=(0.25, 0.75),
        multi_legend_start_factor=0.15,
        title_space_factor=0.95,
        tight_layout_pad=0.5,
        wide_figure_threshold=16.0,
        medium_figure_threshold=12.0,
        wide_spacing_max=0.35,
        medium_spacing_max=0.3,
        wide_span_factor=0.8,
        medium_span_factor=0.7,
    )

    plot_config = PlotConfig(
        layout=(1, 1, {"figsize": (8.0, 6.0)}),
        style={"plot_styles": {"linewidth": 2.0, "alpha": 0.9}, "theme": "line"},
        legend={
            "strategy": "subplot",
            "position": "lower center",
            "positioning_config": positioning_config,
        },
    )

    with FigureManager(plot_config) as fm:
        fm.plot(
            "line",
            0,
            0,
            line_data,
            x="time",
            y="value",
            title="Comprehensive Configuration Example - Basic Time Series",
        )

    show_or_save_plot(fm.fig, args, "01_basic_functionality")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Basic Functionality Example")
    args = parser.parse_args()
    main(args)
