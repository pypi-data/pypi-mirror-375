from typing import Any

from plot_data import ExampleData

from dr_plotter import consts
from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

EXPECTED_CHANNELS = {
    (0, 1): ["hue"],
    (1, 0): ["hue", "style"],
    (1, 1): ["hue", "style"],
}


@inspect_plot_properties()
@verify_plot(
    expected_legends=3,
    expected_channels=EXPECTED_CHANNELS,
    verify_legend_consistency=True,
    expected_legend_entries={
        (0, 1): {"legend_count": 3},
        (1, 0): {"legend_count": 3},
        (1, 1): {"legend_count": 6},
    },
)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 2, "cols": 2, "figsize": (15, 12)})
    ) as fm:
        fm.fig.suptitle("Line Plot Showcase: All Visual Encoding Options", fontsize=16)

        # Basic line
        basic_data = ExampleData.time_series()
        fm.plot("line", 0, 0, basic_data, x="time", y="value", title="Basic Line Plot")

        # Multiple lines with hue
        grouped_data = ExampleData.time_series_grouped()
        fm.plot(
            "line",
            0,
            1,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            title="Multi-Series (hue)",
        )

        # Line style encoding
        fm.plot(
            "line",
            1,
            0,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            style_by="group",
            title="Color + Line Style",
        )

        # Multi-metrics with METRICS encoding
        ml_data = ExampleData.ml_training_curves(epochs=30)
        fm.plot(
            "line",
            1,
            1,
            ml_data,
            x="epoch",
            y=["train_loss", "val_loss"],
            hue_by=consts.METRIC_COL_NAME,
            style_by="learning_rate",
            title="Multi-Metrics (METRICS)",
        )

    show_or_save_plot(fm.fig, args, "10_line_showcase")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Line Plot Showcase")
    args = parser.parse_args()
    main(args)
