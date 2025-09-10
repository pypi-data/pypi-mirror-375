from __future__ import annotations

from dataclasses import fields
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.configs import (
    CycleConfig,
    FacetingConfig,
    GroupingConfig,
    PlotConfig,
)
from dr_plotter.configs.legend_config import LegendStrategy
from dr_plotter.faceting.dimensional_utils import (
    apply_dimensional_filters,
    generate_dimensional_title,
    resolve_dimension_values,
)
from dr_plotter.faceting.faceting_core import (
    _apply_subplot_customization,
    prepare_faceted_subplots,
)
from dr_plotter.faceting.layout_utils import get_grid_dimensions
from dr_plotter.faceting.style_coordination import FacetStyleCoordinator
from dr_plotter.legend_manager import (
    LegendEntry,
    LegendManager,
)
from dr_plotter.plotters.base import BasePlotter
from dr_plotter.style_applicator import StyleApplicator
from dr_plotter.utils import get_axes_from_grid, parse_scale_pair

FACETING_PARAM_NAMES = {f.name for f in fields(FacetingConfig)}
DEFAULT_MARGIN = 0.05


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
            rect = self._get_tight_layout_rect()
            self.fig.tight_layout(
                rect=rect,
                pad=self.layout_config.tight_layout_pad,
            )

    def _get_tight_layout_rect(self) -> tuple[float, float, float, float] | None:
        if self.layout_config.tight_layout_rect is not None:
            return self.layout_config.tight_layout_rect

        has_suptitle = bool(self.layout_config.figure_title)
        has_legend = self.legend_config.legend_strategy in [
            LegendStrategy.FIGURE_BELOW,
            LegendStrategy.GROUPED_BY_CHANNEL,
        ]

        if has_suptitle and has_legend:
            return self.styler.get_style("suptitle_legend_tight_layout_rect")
        elif has_suptitle:
            return self.styler.get_style("suptitle_tight_layout_rect")
        elif has_legend:
            return self.styler.get_style("legend_tight_layout_rect")
        else:
            return None

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

        if self.layout_config.xyscale is not None:
            self._apply_xyscale()

    def _apply_xyscale(self) -> None:
        if isinstance(self.layout_config.xyscale, str):
            x_scale, y_scale = parse_scale_pair(self.layout_config.xyscale)
            for row_idx in range(self.layout_config.rows):
                for col_idx in range(self.layout_config.cols):
                    ax = self.get_axes(row_idx, col_idx)
                    ax.set_xscale(x_scale)
                    ax.set_yscale(y_scale)
        elif isinstance(self.layout_config.xyscale, list):
            for row_idx, row_scales in enumerate(self.layout_config.xyscale):
                for col_idx, scale_pair in enumerate(row_scales):
                    if scale_pair is not None:
                        x_scale, y_scale = parse_scale_pair(scale_pair)
                        ax = self.get_axes(row_idx, col_idx)
                        ax.set_xscale(x_scale)
                        ax.set_yscale(y_scale)

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
            current_xmargin = (
                DEFAULT_MARGIN if layout.xmargin is None else layout.xmargin
            )
            current_ymargin = (
                DEFAULT_MARGIN if layout.ymargin is None else layout.ymargin
            )
            ax.margins(x=current_xmargin, y=current_ymargin)

    def _resolve_faceting_config(
        self,
        faceting: FacetingConfig | None,
        **kwargs: Any,
    ) -> FacetingConfig:
        faceting_params = {k: kwargs[k] for k in FACETING_PARAM_NAMES if k in kwargs}
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

        if (
            faceting is None
            and hasattr(self.config, "faceting")
            and self.config.faceting is not None
        ):
            faceting = self.config.faceting

        config = self._resolve_faceting_config(faceting, **kwargs)
        grid_shape = get_grid_dimensions(data, config)

        data = apply_dimensional_filters(data, config)
        subplot_width = config.subplot_width or self.styler.get_style("subplot_width")
        subplot_height = config.subplot_height or self.styler.get_style(
            "subplot_height"
        )

        if subplot_width is not None and subplot_height is not None:
            self.layout_config.figsize = (
                subplot_width * grid_shape[1],
                subplot_height * grid_shape[0],
            )
            self.layout_config.rows, self.layout_config.cols = grid_shape

            if grid_shape != (
                len(self.axes.flat) if hasattr(self.axes, "flat") else 1,
                1,
            ):
                plt.close(self.fig)
                self.fig, self.axes = plt.subplots(
                    self.layout_config.rows,
                    self.layout_config.cols,
                    constrained_layout=self.layout_config.constrained_layout,
                    **{
                        **self.layout_config.combined_kwargs,
                        "figsize": self.layout_config.figsize,
                    },
                )

        self._validate_grid_dimensions(grid_shape)
        if config.auto_titles:
            self.layout_config.figure_title = generate_dimensional_title(config)

        if not config.rows_by and not config.cols_by and not config.wrap_by:
            self.plot(
                plot_type,
                0,
                0,
                data,
                x=config.x,
                y=config.y,
                hue_by=config.hue_by,
                alpha_by=config.alpha_by,
                size_by=config.size_by,
                marker_by=config.marker_by,
                style_by=config.style_by,
                **kwargs,
            )
            return

        data_subsets = prepare_faceted_subplots(data, config, grid_shape)
        style_coordinator = self._get_or_create_style_coordinator()
        visual_channels = [
            config.hue_by,
            config.alpha_by,
            config.size_by,
            config.marker_by,
            config.style_by,
        ]
        for channel in visual_channels:
            if channel:
                channel_values = resolve_dimension_values(data, channel, config)
                style_coordinator.register_dimension_values(channel, channel_values)
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if not hasattr(FacetingConfig, k)
        }
        full_data = pd.concat(data_subsets.values(), ignore_index=True)
        for (row, col), subplot_data in data_subsets.items():
            self.plot(
                plot_type,
                row,
                col,
                subplot_data,
                x=config.x,
                y=config.y,
                hue_by=config.hue_by,
                alpha_by=config.alpha_by,
                size_by=config.size_by,
                marker_by=config.marker_by,
                style_by=config.style_by,
                style_coordinator=style_coordinator if config.hue_by else None,
                **filtered_kwargs,
            )

            _apply_subplot_customization(self, row, col, config, full_data)

    def _validate_grid_dimensions(self, grid_shape: tuple[int, int]) -> None:
        computed_rows, computed_cols = grid_shape
        figure_rows, figure_cols = self.layout_config.rows, self.layout_config.cols

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
