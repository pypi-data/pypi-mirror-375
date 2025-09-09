import itertools
from typing import Any

import pandas as pd
from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.theme import BASE_THEME, AxesStyles, PlotStyles, Theme


def create_coordinated_theme() -> Theme:
    return Theme(
        name="color_coordination_demo",
        parent=BASE_THEME,
        plot_styles=PlotStyles(
            alpha=0.8,
        ),
        axes_styles=AxesStyles(
            grid_alpha=0.3,
            grid_color="#BDC3C7",
        ),
        default_color="#34495E",
        text_color="#2C3E50",
        hue_cycle=itertools.cycle(["#E74C3C", "#3498DB", "#2ECC71", "#F39C12"]),
    )


def create_color_coordination_example() -> Any:
    coordinated_theme: Theme = create_coordinated_theme()
    data_dict: dict[str, pd.DataFrame] = ExampleData.get_color_coordination_data()

    with FigureManager(
        PlotConfig(
            layout={"rows": 2, "cols": 3, "figsize": (18, 12)},
            style={"theme": coordinated_theme},
        )
    ) as fm:
        fm.fig.suptitle(
            "Example 7: Color Coordination - Multi-Subplot Shared Styling", fontsize=18
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
            s=60,
            title="Scatter: Coordinated Colors & Transparency",
        )

        line_data = data_dict["line_data"]
        fm.plot(
            "line",
            0,
            1,
            line_data,
            x="time",
            y="value",
            hue_by="series",
            linewidth=3,
            title="Line: Same Color Palette Coordination",
        )

        violin_data = data_dict["violin_data"]
        fm.plot(
            "violin",
            0,
            2,
            violin_data,
            x="category",
            y="value",
            hue_by="group",
            showmeans=True,
            title="Violin: Distribution with Coordinated Theme",
        )

        bar_data = data_dict["bar_data"]
        fm.plot(
            "bar",
            1,
            0,
            bar_data,
            x="category",
            y="value",
            color="#3498DB",
            title="Bar: Theme Color Override",
        )

        histogram_data = data_dict["histogram_data"]
        alpha_dist_data = histogram_data[histogram_data["distribution"] == "Alpha"]
        fm.plot(
            "histogram",
            1,
            1,
            alpha_dist_data,
            x="value",
            bins=25,
            color="#E74C3C",
            title="Histogram: Coordinated Single Color",
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
            title="Heatmap: Coordinated Grid & Text Styling",
        )


if __name__ == "__main__":
    create_color_coordination_example()
