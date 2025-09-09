from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.configs import (
    CycleConfig,
    FacetingConfig,
    GroupingConfig,
    PlotConfig,
)
from dr_plotter.faceting.faceting_core import (
    get_grid_dimensions,
    plot_faceted_data,
    prepare_faceted_subplots,
)
from dr_plotter.faceting.style_coordination import FacetStyleCoordinator
from dr_plotter.legend_manager import (
    LegendEntry,
    LegendManager,
)
from dr_plotter.plotters.base import BasePlotter
from dr_plotter.style_applicator import StyleApplicator
from dr_plotter.utils import get_axes_from_grid


class FigureManager:
    def __init__(self, config: PlotConfig | None = None) -> None:
        config = PlotConfig() if config is None else config

        self.layout_config = config.layout
        self.style_config = config.style
        self.legend_config = config.legend
        self.legend_manager = LegendManager(self, self.legend_config)
        self.theme = self.style_config.theme
        self.shared_styling = self.style_config.shared_styling
        self.shared_cycle_config = (
            CycleConfig(self.theme) if self.shared_styling else None
        )

        self.styler = StyleApplicator(
            self.theme,
            config.kwargs,
            grouping_cfg=None,
            figure_manager=self,
        )

        self._facet_grid_info: dict[str, Any] | None = None
        self._facet_style_coordinator: FacetStyleCoordinator | None = None
        self._external_mode = False

        self.fig, self.axes = plt.subplots(
            self.layout_config.rows,
            self.layout_config.cols,
            constrained_layout=self.layout_config.constrained_layout,
            **{
                **self.layout_config.combined_kwargs,
                "figsize": self.layout_config.figsize,
            },
        )

    def _create_figure_axes(self) -> tuple[plt.Figure, plt.Axes, bool]:
        fig, axes = plt.subplots(
            self.layout_config.rows,
            self.layout_config.cols,
            constrained_layout=self.layout_config.constrained_layout,
            **{
                **self.layout_config.combined_kwargs,
                "figsize": self.layout_config.figsize,
            },
        )
        return fig, axes, False

    def __enter__(self) -> FigureManager:
        return self

    def register_legend_entry(self, entry: LegendEntry) -> None:
        self.legend_manager.registry.add_entry(entry)

    def finalize_layout(self) -> None:
        self.legend_manager.finalize()
        self._apply_axis_labels()
        self._apply_axis_scaling()
        self._apply_figure_title()
        if self.layout_config.tight_layout:
            self.fig.tight_layout(
                rect=self.layout_config.tight_layout_rect,
                pad=self.layout_config.tight_layout_pad,
            )

    def _apply_axis_labels(self) -> None:
        if self._external_mode:
            return

        if self.layout_config.x_labels is not None:
            for row_idx, row_labels in enumerate(self.layout_config.x_labels):
                for col_idx, label in enumerate(row_labels):
                    ax = self.get_axes(row_idx, col_idx)
                    if label is not None:
                        ax.set_xlabel(label)
                    else:
                        ax.set_xlabel("")

        if self.layout_config.y_labels is not None:
            for row_idx, row_labels in enumerate(self.layout_config.y_labels):
                for col_idx, label in enumerate(row_labels):
                    ax = self.get_axes(row_idx, col_idx)
                    if label is not None:
                        ax.set_ylabel(label)
                    else:
                        ax.set_ylabel("")

    def _apply_axis_scaling(self) -> None:
        if self._external_mode:
            return

        if self.layout_config.xscale is not None:
            for row_idx in range(self.layout_config.rows):
                for col_idx in range(self.layout_config.cols):
                    ax = self.get_axes(row_idx, col_idx)
                    ax.set_xscale(self.layout_config.xscale)

        if self.layout_config.yscale is not None:
            for row_idx in range(self.layout_config.rows):
                for col_idx in range(self.layout_config.cols):
                    ax = self.get_axes(row_idx, col_idx)
                    ax.set_yscale(self.layout_config.yscale)

    def _apply_figure_title(self) -> None:
        if self._external_mode:
            return

        if self.layout_config.figure_title:
            self.fig.suptitle(
                self.layout_config.figure_title,
                fontsize=self.styler.get_style("suptitle_fontsize"),
                y=self.styler.get_style("suptitle_y"),
            )

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self.finalize_layout()
        return False

    def _has_subplot_titles(self) -> bool:
        if hasattr(self.axes, "flat"):
            axes_to_check = self.axes.flat
        elif hasattr(self.axes, "__iter__") and not isinstance(self.axes, str):
            axes_to_check = self.axes
        else:
            axes_to_check = [self.axes]

        return any(ax.get_title() for ax in axes_to_check)

    def get_axes(self, row: int | None = None, col: int | None = None) -> plt.Axes:
        if self._external_mode:
            return self.axes

        return get_axes_from_grid(self.axes, row, col)

    def _add_plot(
        self,
        plotter_class: type,
        plotter_args: tuple,
        row: int,
        col: int,
        **kwargs: Any,
    ) -> None:
        ax = self.axes if self._external_mode else self.get_axes(row, col)

        kwargs["grouping_cfg"] = GroupingConfig.from_input(kwargs)

        plotter = plotter_class(*plotter_args, figure_manager=self, **kwargs)
        plotter.render(ax)

        self._apply_layout_axis_settings(ax)

    def _apply_layout_axis_settings(self, ax: Any) -> None:
        layout = self.layout_config

        if layout.xlim is not None:
            ax.set_xlim(layout.xlim)

        if layout.ylim is not None:
            ax.set_ylim(layout.ylim)

        if layout.xmargin is not None or layout.ymargin is not None:
            current_xmargin = 0.05 if layout.xmargin is None else layout.xmargin
            current_ymargin = 0.05 if layout.ymargin is None else layout.ymargin
            ax.margins(x=current_xmargin, y=current_ymargin)

    def _resolve_faceting_config(
        self,
        faceting: FacetingConfig | None,
        **kwargs: Any,
    ) -> FacetingConfig:
        faceting_params = {}

        faceting_param_names = {
            "rows",
            "cols",
            "lines",
            "row_order",
            "col_order",
            "lines_order",
            "x",
            "y",
            "x_labels",
            "y_labels",
            "xlim",
            "ylim",
            "subplot_titles",
            "title_template",
            "color_wrap",
            "target_row",
            "target_col",
            "row_titles",
            "col_titles",
            "exterior_x_label",
            "exterior_y_label",
        }

        for param_name in faceting_param_names:
            if param_name in kwargs:
                faceting_params[param_name] = kwargs[param_name]

        if faceting is None:
            return FacetingConfig(**faceting_params)

        config_dict = dict(faceting.__dict__.items())
        config_dict.update({k: v for k, v in faceting_params.items() if v is not None})

        return FacetingConfig(**config_dict)

    def plot_faceted(
        self,
        data: pd.DataFrame,
        plot_type: str,
        faceting: FacetingConfig | None = None,
        **kwargs: Any,
    ) -> None:
        assert not data.empty, "Cannot create faceted plot with empty DataFrame"

        config = self._resolve_faceting_config(faceting, **kwargs)

        assert config.x is not None, "x parameter is required for faceted plotting"
        assert config.y is not None, "y parameter is required for faceted plotting"
        assert config.rows or config.cols, "Must specify rows or cols for faceting"

        if not config.rows and not config.cols:
            self.plot(
                plot_type,
                0,
                0,
                data,
                x=config.x,
                y=config.y,
                hue_by=config.lines,
                **kwargs,
            )
            return

        grid_shape = get_grid_dimensions(data, config)
        self._validate_grid_dimensions(grid_shape)
        data_subsets = prepare_faceted_subplots(data, config, grid_shape)

        style_coordinator = self._get_or_create_style_coordinator()
        if config.lines:
            lines_values = sorted(data[config.lines].unique())
            style_coordinator.register_dimension_values(config.lines, lines_values)

        plot_kwargs = {
            k: v for k, v in kwargs.items() if not hasattr(FacetingConfig, k)
        }

        plot_faceted_data(
            self, data_subsets, plot_type, config, style_coordinator, **plot_kwargs
        )

    def _validate_grid_dimensions(self, grid_shape: tuple[int, int]) -> None:
        computed_rows, computed_cols = grid_shape
        figure_rows, figure_cols = self.layout_config.rows, self.layout_config.cols

        # Allow partial plotting - just make sure the data fits within the figure grid
        if computed_rows > figure_rows or computed_cols > figure_cols:
            assert False, (
                f"Data grid dimensions ({computed_rows}×{computed_cols}) "
                f"exceed figure layout ({figure_rows}×{figure_cols}). "
                f"Increase layout size to fit all data."
            )

    def _get_or_create_style_coordinator(self) -> FacetStyleCoordinator:
        if (
            not hasattr(self, "_facet_style_coordinator")
            or self._facet_style_coordinator is None
        ):
            theme_info = None
            if hasattr(self, "_theme") and self._theme:
                theme_info = {
                    "color_cycle": getattr(self._theme, "color_cycle", None),
                    "marker_cycle": getattr(self._theme, "marker_cycle", None),
                }
            self._facet_style_coordinator = FacetStyleCoordinator(theme=theme_info)
        return self._facet_style_coordinator

    def plot(
        self, plot_type: str, row: int, col: int, *args: Any, **kwargs: Any
    ) -> None:
        plotter_class = BasePlotter.get_plotter(plot_type)
        self._add_plot(plotter_class, args, row, col, **kwargs)
