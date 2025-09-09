from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

EXPECTED_GROUP_COUNT_COLOR = 3
EXPECTED_GROUP_COUNT_CATEGORICAL = 2
EXPECTED_GROUP_COUNT_STYLE = 4

EXPECTED_CHANNELS = {
    (0, 0): ["hue"],
    (0, 1): ["hue", "marker"],
    (1, 0): ["hue"],
    (1, 1): ["hue", "style"],
}


@inspect_plot_properties()
@verify_plot(
    expected_legends=4,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 0): {"hue": 3},
        (0, 1): {"hue": 3, "marker": 2},
        (1, 0): {"hue": 2},
        (1, 1): {"hue": 4, "style": 4},
    },
)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(
            layout={
                "rows": 2,
                "cols": 2,
                "figsize": (15, 12),
                "x_labels": [
                    ["Time (units)", "X Coordinate"],
                    ["Category", "Time (units)"],
                ],
                "y_labels": [["Value", None], ["Distribution", None]],
            }
        )
    ) as fm:
        fm.fig.suptitle(
            "Example 2: Visual Encoding - Color, Marker, and Style Systems", fontsize=16
        )

        # Color encoding with time series
        color_data = ExampleData.time_series_grouped(periods=40, groups=3, seed=201)
        assert "time" in color_data.columns
        assert "value" in color_data.columns
        assert "group" in color_data.columns
        assert len(color_data.groupby("group")) == EXPECTED_GROUP_COUNT_COLOR

        fm.plot(
            "scatter",
            0,
            0,
            color_data,
            x="time",
            y="value",  # REQUIRED: data mapping
            hue_by="group",  # GROUPING: color encoding
            s=60,  # DEFAULT: marker size (theme default)
            alpha=0.8,  # CUSTOM: transparency override
            title="Color Encoding (Hue)",  # STYLING: plot identification
        )

        # Color and marker encoding with complex data
        marker_data = ExampleData.complex_encoding_data(n_samples=90, seed=202)
        assert "x" in marker_data.columns
        assert "y" in marker_data.columns
        assert "experiment" in marker_data.columns
        assert "condition" in marker_data.columns

        fm.plot(
            "scatter",
            0,
            1,
            marker_data,
            x="x",
            y="y",  # REQUIRED: data mapping
            hue_by="experiment",  # GROUPING: color encoding
            marker_by="condition",  # GROUPING: marker encoding
            s=70,  # DEFAULT: marker size (theme default)
            alpha=0.9,  # CUSTOM: transparency override
            title="Color + Marker Encoding",  # STYLING: plot identification
        )

        # Color encoding with categorical data
        categorical_data = ExampleData.grouped_categories(
            n_categories=3, n_groups=2, seed=203
        )
        assert "category" in categorical_data.columns
        assert "value" in categorical_data.columns
        assert "group" in categorical_data.columns
        assert (
            len(categorical_data.groupby("group")) == EXPECTED_GROUP_COUNT_CATEGORICAL
        )

        fm.plot(
            "violin",
            1,
            0,
            categorical_data,
            x="category",
            y="value",  # REQUIRED: data mapping
            hue_by="group",  # GROUPING: color encoding
            showmeans=True,  # DEFAULT: show means (theme default)
            title="Categorical Color Encoding",  # STYLING: plot identification
        )

        # Color and style encoding with line plot
        style_data = ExampleData.time_series_grouped(periods=35, groups=4, seed=204)
        assert "time" in style_data.columns
        assert "value" in style_data.columns
        assert "group" in style_data.columns
        assert len(style_data.groupby("group")) == EXPECTED_GROUP_COUNT_STYLE

        fm.plot(
            "line",
            1,
            1,
            style_data,
            x="time",
            y="value",  # REQUIRED: data mapping
            hue_by="group",  # GROUPING: color encoding
            style_by="group",  # GROUPING: line style encoding
            linewidth=2.5,  # DEFAULT: line width (theme default)
            alpha=0.8,  # CUSTOM: transparency override
            title="Color + Style Encoding",  # STYLING: plot identification
        )

    show_or_save_plot(fm.fig, args, "02_visual_encoding")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Visual Encoding Systems Example")
    args = parser.parse_args()
    main(args)
