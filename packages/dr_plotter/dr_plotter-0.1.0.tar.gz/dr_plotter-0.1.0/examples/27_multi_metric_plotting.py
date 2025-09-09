"""
Example 6: Multi-Metric Plotting - METRICS constant.
Demonstrates plotting multiple y-columns with the METRICS constant.
"""

from typing import Any

from plot_data import ExampleData

from dr_plotter import consts
from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

FILTER_LEARNING_RATE = 0.01

EXPECTED_CHANNELS = {
    (0, 0): ["hue"],
    (0, 1): ["hue", "style"],
    (1, 0): ["hue", "style"],
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
        (1, 0): {"hue": 3},
        (1, 1): {"hue": 3},
    },
)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 2, "cols": 2, "figsize": (15, 12)})
    ) as fm:
        fm.fig.suptitle("Multi-Metrics: Using the METRICS Constant", fontsize=16)

        # ML training data with multiple metrics
        ml_data = ExampleData.ml_training_curves()

        # Basic multi-metrics: color by METRICS
        # (filter to single learning rate for clarity)
        single_lr_data = ml_data[
            ml_data["learning_rate"] == FILTER_LEARNING_RATE
        ].copy()
        fm.plot(
            "line",
            0,
            0,
            single_lr_data,
            x="epoch",
            y=["train_loss", "val_loss"],
            hue_by=consts.METRIC_COL_NAME,
            title="Loss Metrics (hue_by=METRICS)",
        )

        # Multi-metrics with additional grouping
        fm.plot(
            "line",
            0,
            1,
            ml_data,
            x="epoch",
            y=["train_loss", "val_loss"],
            hue_by=consts.METRIC_COL_NAME,
            style_by="learning_rate",
            title="Loss + Learning Rate",
        )

        # Accuracy metrics
        fm.plot(
            "line",
            1,
            0,
            ml_data,
            x="epoch",
            y=["train_accuracy", "val_accuracy"],
            hue_by="learning_rate",
            style_by=consts.METRIC_COL_NAME,
            title="Accuracy (style_by=METRICS)",
        )

        # Generic multi-metric data
        multi_data = ExampleData.multi_metric_data()
        fm.plot(
            "line",
            1,
            1,
            multi_data,
            x="x",
            y=["metric_a", "metric_b", "metric_c"],
            hue_by=consts.METRIC_COL_NAME,
            title="Generic Multi-Metrics",
        )

    show_or_save_plot(fm.fig, args, "06_multi_metric_plotting")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Multi-Metric Plotting Example")
    args = parser.parse_args()
    main(args)
