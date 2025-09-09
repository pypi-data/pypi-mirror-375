from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot


@inspect_plot_properties()
@verify_plot(expected_legends=0)
def main(args: Any) -> Any:
    with FigureManager(
        PlotConfig(layout={"rows": 1, "cols": 2, "figsize": (15, 6)})
    ) as fm:
        fm.fig.suptitle("Contour Plot Showcase: Density Visualization", fontsize=16)

        # Basic contour plot
        mixture_data = ExampleData.gaussian_mixture(n_components=2)
        fm.plot("contour", 0, 0, mixture_data, x="x", y="y", title="2-Component GMM")

        # More complex mixture
        complex_mixture = ExampleData.gaussian_mixture(n_components=3)
        fm.plot("contour", 0, 1, complex_mixture, x="x", y="y", title="3-Component GMM")

    show_or_save_plot(fm.fig, args, "14_contour_showcase")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Contour Plot Showcase")
    args = parser.parse_args()
    main(args)
