from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

EXPECTED_COORD_GROUP_COUNT = 3

EXPECTED_CHANNELS = {
    (0, 0): ["hue"],
    (0, 1): ["hue", "marker"],
    (1, 0): ["hue"],
    (1, 1): ["hue"],
}


@inspect_plot_properties()
@verify_plot(
    expected_legends=4,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 0): {"hue": 2},
        (0, 1): {"hue": 3, "marker": 2},
        (1, 0): {"hue": 3},
        (1, 1): {"hue": 3},
    },
)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(
            layout={
                "rows": 2,
                "cols": 2,
                "figsize": (16, 12),
                "x_labels": [[None, None], ["Training Epoch", "Time (units)"]],
                "y_labels": [["Metric A", "Y Coordinate"], ["Training Loss", None]],
            }
        )
    ) as fm:
        fm.fig.suptitle(
            "Example 3: Layout & Composition - Multi-Subplot Coordination", fontsize=16
        )

        metric_data = ExampleData.multi_metric_data(n_samples=60, seed=301)
        assert "x" in metric_data.columns
        assert "metric_a" in metric_data.columns
        assert "category" in metric_data.columns

        fm.plot(
            "scatter",
            0,
            0,
            metric_data,
            x="x",
            y="metric_a",  # REQUIRED: data mapping
            hue_by="category",  # GROUPING: color encoding
            s=50,  # DEFAULT: marker size (theme default)
            alpha=0.8,  # CUSTOM: transparency override
            title="Multi-Metric Layout",  # STYLING: plot identification
        )

        layout_data = ExampleData.complex_encoding_data(n_samples=100, seed=302)
        assert "x" in layout_data.columns
        assert "y" in layout_data.columns
        assert "experiment" in layout_data.columns
        assert "condition" in layout_data.columns

        fm.plot(
            "scatter",
            0,
            1,
            layout_data,
            x="x",
            y="y",  # REQUIRED: data mapping
            hue_by="experiment",  # GROUPING: color encoding
            marker_by="condition",  # GROUPING: marker encoding
            s=60,  # DEFAULT: marker size (theme default)
            alpha=0.7,  # CUSTOM: transparency override
            title="Complex Data Coordination",  # STYLING: plot identification
        )

        training_data = ExampleData.ml_training_curves(epochs=30, seed=303)
        assert "epoch" in training_data.columns
        assert "train_loss" in training_data.columns
        assert "learning_rate" in training_data.columns

        fm.plot(
            "line",
            1,
            0,
            training_data,
            x="epoch",
            y="train_loss",  # REQUIRED: data mapping
            hue_by="learning_rate",  # GROUPING: color encoding
            linewidth=2.0,  # DEFAULT: line width (theme default)
            alpha=0.9,  # CUSTOM: transparency override
            title="Training Curves Layout",  # STYLING: plot identification
        )

        coord_data = ExampleData.time_series_grouped(periods=25, groups=3, seed=304)
        assert "time" in coord_data.columns
        assert "value" in coord_data.columns
        assert "group" in coord_data.columns
        assert len(coord_data.groupby("group")) == EXPECTED_COORD_GROUP_COUNT

        fm.plot(
            "line",
            1,
            1,
            coord_data,
            x="time",
            y="value",  # REQUIRED: data mapping
            hue_by="group",  # GROUPING: color encoding
            linewidth=2.5,  # DEFAULT: line width (theme default)
            alpha=0.8,  # CUSTOM: transparency override
            title="Coordinated Time Series",  # STYLING: plot identification
        )

    show_or_save_plot(fm.fig, args, "03_layout_composition")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Layout & Composition Example")
    args = parser.parse_args()
    main(args)
