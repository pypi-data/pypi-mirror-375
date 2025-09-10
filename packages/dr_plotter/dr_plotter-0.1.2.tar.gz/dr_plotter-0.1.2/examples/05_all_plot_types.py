from typing import Any

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.plot_data import experimental_data, matrix_data
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

EXPECTED_CHANNELS = {
    (0, 0): ["hue"],
    (0, 1): ["hue"],
    (0, 2): ["hue"],
    (1, 0): [],
    (1, 1): ["hue"],
    (1, 2): [],
    (2, 0): [],
    (2, 1): [],
}

SEED = 100
SAMPLES = 100
TIME_POINTS = 15
HEATMAP_DIM = 5

BINARY_GROUPS = ["Group_A", "Group_B"]
THREE_CATEGORIES = ["Cat_A", "Cat_B", "Cat_C"]


@inspect_plot_properties()
@verify_plot(
    expected_legends=4,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 0): {"hue": 2},
        (0, 1): {"hue": 2},
        (0, 2): {"hue": 2},
        (1, 1): {"hue": 2},
    },
)
def main(args: Any) -> Any:
    scatter_data = experimental_data(
        pattern_type="categorical", n_samples=SAMPLES, seed=SEED
    )
    line_data = experimental_data(
        pattern_type="time_series",
        time_points=TIME_POINTS,
        groups=BINARY_GROUPS,
        seed=SEED,
    )
    bar_data = experimental_data(
        pattern_type="categorical",
        groups=BINARY_GROUPS,
        categories=THREE_CATEGORIES,
        seed=SEED,
    )
    histogram_data = experimental_data(
        pattern_type="distribution", n_samples=SAMPLES, seed=SEED
    )
    violin_data = experimental_data(
        pattern_type="categorical",
        groups=BINARY_GROUPS,
        categories=THREE_CATEGORIES,
        seed=SEED,
    )
    heatmap_data = matrix_data(rows=HEATMAP_DIM, cols=HEATMAP_DIM, seed=SEED)
    contour_data = matrix_data(pattern_type="contour", rows=SAMPLES, seed=SEED)
    bump_data = experimental_data(
        pattern_type="time_series",
        categories=THREE_CATEGORIES,
        time_points=TIME_POINTS,
        seed=SEED,
    )

    with FigureManager(
        PlotConfig(
            layout={
                "rows": 3,
                "cols": 3,
                "figsize": (14, 14),
                "x_labels": [
                    [None, None, None],
                    [None, None, None],
                    ["X Coordinate", "Category", "Column"],
                ],
                "y_labels": [
                    ["Y Coordinate", "Value", "Count"],
                    ["Y Continuous", "Response", None],
                    ["Count", None, None],
                ],
            }
        )
    ) as fm:
        fm.fig.suptitle(
            "Example 5: All Plot Types - Systematic Verification of 8 Plotters",
            fontsize=20,
        )

        fm.plot(
            "scatter",
            0,
            0,
            scatter_data,
            x="x_continuous",
            y="y_continuous",
            hue_by="category",
            s=75,
            alpha=0.8,
            title="Scatter: Hue Encoding with Size & Transparency",
        )

        fm.plot(
            "line",
            0,
            1,
            line_data,
            x="time_point",
            y="value",
            hue_by="group",
            linewidth=3,
            linestyle="-",
            title="Line: Connected Points with Style Variation",
        )

        fm.plot(
            "bar",
            0,
            2,
            bar_data,
            x="category",
            y="value",
            hue_by="group",
            alpha=0.9,
            title="Bar: Categorical Data with Color Variation",
        )

        fm.plot(
            "histogram",
            1,
            0,
            histogram_data,
            x="value",
            bins=30,
            alpha=0.7,
            color="steelblue",
            title="Histogram: Distribution with Bin Customization",
        )

        fm.plot(
            "violin",
            1,
            1,
            violin_data,
            x="category",
            y="value",
            hue_by="group",
            alpha=0.8,
            showmeans=True,
            title="Violin: Distribution Shape with Style Variation",
        )

        fm.plot(
            "heatmap",
            1,
            2,
            heatmap_data,
            x="column",
            y="row",
            values="value",
            cmap="plasma",
            annot=False,
            title="Heatmap: 2D Data with Colormap Customization",
        )

        fm.plot(
            "contour",
            2,
            0,
            contour_data,
            x="x",
            y="y",
            levels=8,
            alpha=0.8,
            title="Contour: Density Lines with Level Customization",
        )

        fm.plot(
            "bump",
            2,
            1,
            bump_data,
            time_col="time_point",
            value_col="value",
            category_col="category",
            marker="o",
            linewidth=2,
            title="Bump: Ranking Plot with Marker Variation",
        )

    show_or_save_plot(fm.fig, args, "05_all_plot_types")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="All Plot Types Example")
    args = parser.parse_args()
    main(args)
