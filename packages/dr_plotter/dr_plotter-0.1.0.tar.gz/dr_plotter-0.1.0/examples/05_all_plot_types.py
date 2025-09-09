from typing import Any

import pandas as pd
from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
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
    data_dict: dict[str, pd.DataFrame] = ExampleData.get_all_plot_types_data()

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
                    ["Y Coordinate", "Response", None],
                    ["Count", None, None],
                ],
            }
        )
    ) as fm:
        fm.fig.suptitle(
            "Example 5: All Plot Types - Systematic Verification of 8 Plotters",
            fontsize=20,
        )

        scatter_data = data_dict["scatter_data"]
        fm.plot(
            "scatter",
            0,
            0,
            scatter_data,
            x="x",
            y="y",
            hue_by="category",
            s=75,
            alpha=0.8,
            title="Scatter: Hue Encoding with Size & Transparency",
        )

        line_data = data_dict["line_data"]
        fm.plot(
            "line",
            0,
            1,
            line_data,
            x="time",
            y="value",
            hue_by="group",
            linewidth=3,
            linestyle="-",
            title="Line: Connected Points with Style Variation",
        )

        bar_data = data_dict["bar_data"]
        fm.plot(
            "bar",
            0,
            2,
            bar_data,
            x="category",
            y="value",
            hue_by="category_group",
            alpha=0.9,
            title="Bar: Categorical Data with Color Variation",
        )

        histogram_data = data_dict["histogram_data"]
        single_dist_data = histogram_data[histogram_data["distribution"] == "Normal"]
        fm.plot(
            "histogram",
            1,
            0,
            single_dist_data,
            x="value",
            bins=30,
            alpha=0.7,
            color="steelblue",
            title="Histogram: Distribution with Bin Customization",
        )

        violin_data = data_dict["violin_data"]
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

        heatmap_data = data_dict["heatmap_data"]
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

        contour_data = data_dict["contour_data"]
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

        bump_data = data_dict["bump_data"]
        fm.plot(
            "bump",
            2,
            1,
            bump_data,
            time_col="time",
            value_col="score",
            category_col="category",
            marker="o",
            linewidth=2,
            title="Bump: Ranking Plot with Marker Variation",
        )

        ax_summary = fm.fig.add_subplot(3, 3, 9)
        ax_summary.text(
            0.1,
            0.8,
            "Summary:",
            fontsize=16,
            fontweight="bold",
            transform=ax_summary.transAxes,
        )
        ax_summary.text(
            0.1,
            0.7,
            "• 8 plotters verified",
            fontsize=12,
            transform=ax_summary.transAxes,
        )
        ax_summary.text(
            0.1,
            0.6,
            "• Parameter variations tested",
            fontsize=12,
            transform=ax_summary.transAxes,
        )
        ax_summary.text(
            0.1,
            0.5,
            "• Legend generation confirmed",
            fontsize=12,
            transform=ax_summary.transAxes,
        )
        ax_summary.text(
            0.1,
            0.4,
            "• Theme system integration",
            fontsize=12,
            transform=ax_summary.transAxes,
        )
        ax_summary.text(
            0.1,
            0.3,
            "• StyleApplicator pipeline",
            fontsize=12,
            transform=ax_summary.transAxes,
        )
        ax_summary.text(
            0.1,
            0.2,
            "• FigureManager coordination",
            fontsize=12,
            transform=ax_summary.transAxes,
        )
        ax_summary.set_xlim(0, 1)
        ax_summary.set_ylim(0, 1)
        ax_summary.axis("off")
        ax_summary.set_title("Architecture Integration", fontsize=14, fontweight="bold")

    show_or_save_plot(fm.fig, args, "05_all_plot_types")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="All Plot Types Example")
    args = parser.parse_args()
    main(args)
