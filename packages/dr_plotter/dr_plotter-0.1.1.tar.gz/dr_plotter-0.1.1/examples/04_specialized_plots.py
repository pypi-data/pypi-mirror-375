from typing import Any

from dr_plotter.scripting import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot

EXPECTED_CONTOUR_SAMPLE_COUNT = 400
EXPECTED_VIOLIN_GROUP_COUNT = 2

EXPECTED_CHANNELS = {
    (0, 0): [],  # Heatmap
    (0, 1): [],  # Contour
    (1, 0): ["hue"],  # Violin with grouping
    (1, 1): [],  # Histogram without grouping
}


@inspect_plot_properties()
@verify_plot(
    expected_legends=1,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (1, 0): {"hue": 2},
    },
)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(
            layout={
                "rows": 2,
                "cols": 2,
                "figsize": (16, 12),
                "x_labels": [[None, None], ["Distribution Values", "Category"]],
                "y_labels": [["Row Index", "Y Coordinate"], ["Frequency", None]],
            }
        )
    ) as fm:
        fm.fig.suptitle(
            "Example 4: Specialized Plots - Heatmap, Contour, and Distribution Types",
            fontsize=16,
        )

        # Subplot (0,0): Heatmap Specialized Data
        heatmap_data = ExampleData.heatmap_data(rows=8, cols=6, seed=401)
        assert "row" in heatmap_data.columns
        assert "column" in heatmap_data.columns
        assert "value" in heatmap_data.columns
        assert len(heatmap_data) == 8 * 6

        fm.plot(
            "heatmap",
            0,
            0,
            heatmap_data,
            x="column",
            y="row",
            values="value",  # REQUIRED: heatmap data mapping
            cmap="viridis",  # DEFAULT: colormap (theme default)
            annot=True,  # CUSTOM: show cell annotations
            title="Heatmap Specialized Data",  # STYLING: plot identification
        )

        # Subplot (0,1): Contour Density Visualization
        contour_data = ExampleData.gaussian_mixture(
            n_components=2, n_samples=400, seed=402
        )
        assert "x" in contour_data.columns
        assert "y" in contour_data.columns
        assert len(contour_data) == EXPECTED_CONTOUR_SAMPLE_COUNT

        fm.plot(
            "contour",
            0,
            1,
            contour_data,
            x="x",
            y="y",  # REQUIRED: 2D data mapping
            levels=10,  # DEFAULT: contour levels (theme default)
            alpha=0.7,  # CUSTOM: contour transparency
            title="Contour Density Plot",  # STYLING: plot identification
        )

        # Subplot (1,0): Violin Distribution Comparison
        violin_data = ExampleData.grouped_categories(
            n_categories=4, n_groups=2, n_per_combo=25, seed=403
        )
        assert "category" in violin_data.columns
        assert "value" in violin_data.columns
        assert "group" in violin_data.columns
        assert len(violin_data.groupby("group")) == EXPECTED_VIOLIN_GROUP_COUNT

        fm.plot(
            "violin",
            1,
            0,
            violin_data,
            x="category",
            y="value",  # REQUIRED: categorical data mapping
            hue_by="group",  # GROUPING: color encoding
            showmeans=True,  # DEFAULT: show means (theme default)
            alpha=0.8,  # CUSTOM: violin transparency
            title="Violin Distribution Groups",  # STYLING: plot identification
        )

        # Subplot (1,1): Simple Distribution Histogram
        hist_data = ExampleData.distribution_data(
            n_samples=500, distributions=1, seed=404
        )
        assert "values" in hist_data.columns

        fm.plot(
            "histogram",
            1,
            1,
            hist_data,
            x="values",  # REQUIRED: distribution data mapping
            bins=25,  # DEFAULT: bin count (theme default)
            alpha=0.7,  # CUSTOM: histogram transparency
            title="Distribution Histogram",  # STYLING: plot identification
        )

    show_or_save_plot(fm.fig, args, "04_specialized_plots")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Specialized Plot Types Example")
    args = parser.parse_args()
    main(args)
