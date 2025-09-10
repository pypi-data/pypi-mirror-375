from typing import Any, ClassVar

import pandas as pd
from dr_plotter.scripting import ExampleData

from dr_plotter import consts
from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.plotters.base import BasePlotter
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties, verify_plot
from dr_plotter.theme import BASE_THEME, PlotStyles, Theme
from dr_plotter.types import VisualChannel

# Create a custom theme following the expected pattern
ERRORBAR_THEME = Theme(
    name="errorbar",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        capsize=5,
        capthick=2,
        elinewidth=1.5,
        alpha=0.8,
        fmt="o",
    ),
)


class ErrorBarPlotter(BasePlotter):
    plotter_name: str = "errorbar"
    plotter_params: ClassVar[list[str]] = [
        "error"
    ]  # Only custom params, x/y are handled by base
    param_mapping: ClassVar[dict[str, str]] = {"error": "error"}
    enabled_channels: ClassVar[set[VisualChannel]] = (
        set()
    )  # No visual channels for simplicity
    default_theme: ClassVar[Theme] = ERRORBAR_THEME
    use_style_applicator: ClassVar[bool] = True
    use_legend_manager: ClassVar[bool] = True

    # Define what styling attributes are available
    component_schema: ClassVar[dict[str, dict[str, set[str]]]] = {
        "plot": {
            "main": {
                "capsize",
                "capthick",
                "elinewidth",
                "alpha",
                "color",
                "fmt",
            }
        },
    }

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        """Render the error bar plot using standardized column names."""
        # Get error values - check if custom error column is provided
        error_col = self.kwargs.get("error")
        if error_col and error_col in data.columns:
            yerr = data[error_col]
        else:
            # Default: use 10% of absolute y values as error
            yerr = abs(data[consts.Y_COL_NAME]) * 0.1 + 0.1

        # Remove custom parameters that matplotlib doesn't understand
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "error"}

        # Use standardized column names from consts
        ax.errorbar(
            data[consts.X_COL_NAME],
            data[consts.Y_COL_NAME],
            yerr=yerr,
            **filtered_kwargs,
        )


@inspect_plot_properties()
@verify_plot(expected_legends=0)
def main(args: Any) -> Any:
    # Verify our custom plotter is registered
    from dr_plotter.plotters import BasePlotter

    print("📋 Available plotters after custom registration:")
    for plotter_type in BasePlotter.list_plotters():
        print(f"   - {plotter_type}")
    print()

    # Create test data with error values
    base_data = ExampleData.categorical_data()
    error_data = (
        base_data.groupby("category").agg({"value": ["mean", "std"]}).reset_index()
    )

    # Flatten column names
    error_data.columns = ["category", "mean_value", "error"]

    with FigureManager(
        PlotConfig(layout={"rows": 1, "cols": 2, "figsize": (12, 5)})
    ) as fm:
        fm.fig.suptitle("Custom Plotter: Error Bar Plots", fontsize=16)

        # Use custom plotter via registry
        fm.plot(
            "errorbar",
            0,
            0,
            error_data,
            x="category",
            y="mean_value",
            error="error",
            title="Custom Error Bars (with std)",
        )

        # Use custom plotter with default errors
        simple_data = ExampleData.time_series(periods=20)
        fm.plot(
            "errorbar",
            0,
            1,
            simple_data,
            x="time",
            y="value",
            title="Custom Error Bars (default 10%)",
        )

    show_or_save_plot(fm.fig, args, "17_custom_plotters")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Custom Plotter Example")
    args = parser.parse_args()
    main(args)
