from __future__ import annotations

from typing import Any, ClassVar

import pandas as pd

from dr_plotter import consts
from dr_plotter.channel_metadata import ChannelRegistry
from dr_plotter.configs import GroupingConfig
from dr_plotter.style_engine import StyleEngine
from dr_plotter.style_applicator import StyleApplicator
from dr_plotter.styling_utils import (
    apply_grid_styling,
    apply_title_styling,
    apply_xlabel_styling,
    apply_ylabel_styling,
)
from dr_plotter.theme import BASE_THEME, Theme
from dr_plotter.types import (
    ColName,
    ComponentSchema,
    GroupContext,
    GroupInfo,
    Phase,
    VisualChannel,
)


def as_list(x: Any | list[Any] | None) -> list[Any]:
    return x if isinstance(x, list) else [x]


def fmt_txt(text: str) -> str:
    if text is not None:
        return text.replace("_", " ").title()


def ylabel_from_metrics(metrics: list[ColName]) -> str | None:
    if len(metrics) != 1:
        return None
    return metrics[0]


class BasePlotter:
    _registry: ClassVar[dict[str, type]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        BasePlotter._registry[cls.plotter_name] = cls

    @classmethod
    def get_plotter(cls, plot_type: str) -> type:
        return cls._registry[plot_type]

    @classmethod
    def list_plotters(cls) -> list[str]:
        return sorted(cls._registry.keys())

    plotter_name: str = "base"
    plotter_params: ClassVar[list[str]] = []
    enabled_channels: ClassVar[set[VisualChannel]] = set()
    default_theme: ClassVar[Theme] = BASE_THEME
    supports_legend: bool = True
    supports_grouped: ClassVar[bool] = True

    component_schema: ClassVar[dict[Phase, ComponentSchema]] = {
        "plot": {"main": set()},
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
        },
    }

    def __init__(
        self,
        data: pd.DataFrame,
        grouping_cfg: GroupingConfig,
        theme: Theme | None = None,
        figure_manager: Any | None = None,
        **kwargs: Any,
    ) -> None:
        self.raw_data: pd.DataFrame = data
        self.kwargs: dict[str, Any] = kwargs
        self.figure_manager: Any | None = figure_manager
        grouping_cfg.validate_against_enabled(self.__class__.enabled_channels)
        self.grouping_params: GroupingConfig = grouping_cfg
        self.theme = self.__class__.default_theme if theme is None else theme
        self.style_engine: StyleEngine = StyleEngine(self.theme, self.figure_manager)
        self.styler: StyleApplicator = StyleApplicator(
            self.theme,
            self.kwargs,
            self.grouping_params,
            figure_manager=self.figure_manager,
            plot_type=self.__class__.plotter_name,
            style_engine=self.style_engine,
        )
        self.plot_data: pd.DataFrame | None = None
        self._initialize_subplot_specific_params()

        self.styler.register_post_processor(
            self.__class__.plotter_name, "title", self._style_title
        )
        self.styler.register_post_processor(
            self.__class__.plotter_name, "xlabel", self._style_xlabel
        )
        self.styler.register_post_processor(
            self.__class__.plotter_name, "ylabel", self._style_ylabel
        )
        self.styler.register_post_processor(
            self.__class__.plotter_name, "grid", self._style_grid
        )

        self.x_col: ColName | None = self._get_x_metric_column_name()
        self.y_cols: list[ColName] = self._get_y_metric_column_names()

    @property
    def _has_groups(self) -> bool:
        return len(self.grouping_params.active_channels) > 0

    @property
    def _multi_metric(self) -> bool:
        return len(self._get_y_metric_column_names()) > 1

    def _plot_specific_data_prep(self) -> None:
        pass

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        pass

    # TODO: Evaluate if group_position is needed for positioning logic
    def _draw_grouped(
        self,
        ax: Any,
        data: pd.DataFrame,
        group_position: dict[str, Any],  # noqa: ARG002
        **kwargs: Any,
    ) -> None:
        if not self.supports_grouped:
            self._draw(ax, self.plot_data, **kwargs)
        else:
            self._draw(ax, data, **kwargs)

    def _setup_continuous_channels(self) -> None:
        for channel in self.grouping_params.active_channels_ordered:
            spec = ChannelRegistry.get_spec(channel)
            if spec.channel_type == "continuous":
                column = getattr(self.grouping_params, channel)
                if column and column in self.plot_data.columns:
                    values = self.plot_data[column].dropna().tolist()
                    sample_values = values[:5]
                    assert all(
                        isinstance(v, (int, float))
                        or (
                            isinstance(v, str)
                            and v.replace(".", "").replace("-", "").isdigit()
                        )
                        for v in sample_values
                    ), f"Column {column} contains non-numeric values"

                    if values:
                        self.style_engine.set_continuous_range(channel, column, values)

    def render(self, ax: Any) -> None:
        self.prepare_data()
        self.current_axis = ax
        self._setup_continuous_channels()

        if self._has_groups:
            self._render_with_grouped_method(ax)
        else:
            component_styles = self.styler.get_component_styles(
                self.__class__.plotter_name
            )
            style_kwargs = component_styles.get("main", {})

            self._draw(
                ax,
                self.plot_data,
                **style_kwargs,
            )

        if self._has_groups:
            self.styler.clear_group_context()

        self._apply_styling(ax)

    def prepare_data(self) -> None:
        self.plot_data = self.raw_data.copy()

        if self.x_col is not None:
            self.plot_data = self.plot_data.rename(
                columns={self.x_col: consts.X_COL_NAME}
            )

        if len(self.y_cols) > 0:
            df_cols = set(self.plot_data.columns)
            value_cols = set(self.y_cols)
            assert len(value_cols - df_cols) == 0, "All metrics must be in the data"
            id_cols = df_cols - value_cols
            self.plot_data = pd.melt(
                self.plot_data,
                id_vars=id_cols,
                value_vars=self.y_cols,
                var_name=consts.METRIC_COL_NAME,
                value_name=consts.Y_COL_NAME,
            )

        self._plot_specific_data_prep()

    def _resolve_phase_config(self, phase: str, **context: Any) -> dict[str, Any]:
        phase_params = self.component_schema.get("plot", {}).get(phase, set())
        config = {}

        for param in phase_params:
            sources = [
                lambda k: context.get(k),
                lambda k: self.kwargs.get(f"{phase}_{k}"),
                lambda k: self.kwargs.get(k),
                lambda k: self.styler.get_style(f"{phase}_{k}"),
                lambda k: self.styler.get_style(k),
            ]

            for source in sources:
                value = source(param)
                if value is not None:
                    config[param] = value
                    break

        config.update(self._resolve_computed_parameters(phase, context))
        return config

    # TODO: Consider removing unused parameters if not needed by subclasses
    def _resolve_computed_parameters(self, phase: str, context: dict) -> dict[str, Any]:  # noqa: ARG002
        return {}

    # The _build_plot_args method has been removed as part of the configuration
    # system refactoring.
    # All plotters now use _resolve_phase_config instead.

    def _should_create_legend(self) -> bool:
        if not self.supports_legend:
            return False
        legend_param = self.kwargs.get("legend", self.styler.get_style("legend"))
        return legend_param is not False

    def _register_legend_entry_if_valid(self, artist: Any, label: str | None) -> None:
        if not self._should_create_legend():
            return
        if self.figure_manager and label and artist:
            entry = self.styler.create_legend_entry(artist, label, self.current_axis)
            if entry:
                self.figure_manager.register_legend_entry(entry)

    def _apply_styling(self, ax: Any) -> None:
        artists = {
            "title": ax,
            "xlabel": ax,
            "ylabel": ax,
            "grid": ax,
        }
        self.styler.apply_post_processing(self.__class__.plotter_name, artists)

    def _render_with_grouped_method(self, ax: Any) -> None:
        grouped_data = self._process_grouped_data()
        x_categories = self._extract_x_categories()

        for group_index, group_info in enumerate(grouped_data):
            group_context = self._setup_group_context(
                group_info, group_index, len(grouped_data)
            )
            plot_kwargs = self._resolve_group_plot_kwargs(group_context)
            group_position = self._calculate_group_position(
                group_index, len(grouped_data), x_categories
            )

            self._draw_grouped(ax, group_context["data"], group_position, **plot_kwargs)

    def _process_grouped_data(self) -> list[GroupInfo]:
        categorical_cols = []
        for channel, column in self.grouping_params.active.items():
            spec = ChannelRegistry.get_spec(channel)
            if spec.channel_type == "categorical":
                categorical_cols.append(column)

        if categorical_cols:
            grouped = self.plot_data.groupby(categorical_cols, observed=False)
            return list(grouped)
        else:
            return [(None, self.plot_data)]

    def _extract_x_categories(self) -> Any | None:
        if hasattr(self, "x") and self.x_col:
            return self.plot_data[self.x_col].unique()
        return None

    # TODO: Check if group_index/n_groups are needed for future group positioning
    def _setup_group_context(
        self,
        group_info: GroupInfo,
        group_index: int,  # noqa: ARG002
        n_groups: int,  # noqa: ARG002
    ) -> GroupContext:
        name, group_data = group_info

        categorical_cols = []
        for channel, column in self.grouping_params.active.items():
            spec = ChannelRegistry.get_spec(channel)
            if spec.channel_type == "categorical":
                categorical_cols.append(column)

        if name is None:
            group_values = {}
        elif isinstance(name, tuple):
            group_values = dict(zip(categorical_cols, name))
        else:
            group_values = {categorical_cols[0]: name} if categorical_cols else {}

        return {
            "name": name,
            "data": group_data,
            "values": group_values,
            "categorical_cols": categorical_cols,
        }

    def _resolve_group_plot_kwargs(self, group_context: GroupContext) -> dict[str, Any]:
        self.styler.set_group_context(group_context["values"])
        component_styles = self.styler.get_component_styles(self.__class__.plotter_name)
        plot_kwargs = component_styles.get("main", {})
        plot_kwargs["label"] = self._build_group_label(
            group_context["name"], group_context["categorical_cols"]
        )

        return plot_kwargs

    def _calculate_group_position(
        self, group_index: int, n_groups: int, x_categories: Any | None = None
    ) -> dict[str, Any]:
        width = 0.8 / n_groups
        offset = width * (group_index - n_groups / 2 + 0.5)

        return {
            "index": group_index,
            "total": n_groups,
            "width": width,
            "offset": offset,
            "x_categories": x_categories,
        }

    def _get_x_metric_column_name(self) -> ColName | None:
        subplotter_x_metric = "x"
        return self.kwargs.get(subplotter_x_metric)

    def _get_y_metric_column_names(self) -> list[ColName]:
        subplotter_y_metric = "y"
        metric_col_name = self.kwargs.get(subplotter_y_metric)
        return as_list(metric_col_name if metric_col_name is not None else [])

    def _initialize_subplot_specific_params(self) -> None:
        for param in self.__class__.plotter_params:
            setattr(self, param, self.kwargs.get(param))

    def _build_group_label(self, name: Any, group_cols: list[str]) -> str:
        if isinstance(name, tuple):
            if len(name) == 1:
                return str(name[0])
            label_parts = []
            for col, val in zip(group_cols, name):
                if col == consts.METRIC_COL_NAME:
                    label_parts.append(str(val))
                else:
                    label_parts.append(f"{col}={val}")
            return ", ".join(label_parts)
        return str(name)

    def _style_title(self, ax: Any, styles: dict[str, Any]) -> None:
        title_text = styles.get("text", self.styler.get_style("title"))
        apply_title_styling(ax, self.styler, title_text)

    def _style_xlabel(self, ax: Any, styles: dict[str, Any]) -> None:
        xlabel_text = styles.get("text", self.styler.get_style("xlabel", None))
        apply_xlabel_styling(ax, self.styler, xlabel_text)

    def _style_ylabel(self, ax: Any, styles: dict[str, Any]) -> None:
        ylabel_text = styles.get("text", self.styler.get_style("ylabel", None))
        apply_ylabel_styling(ax, self.styler, ylabel_text)

    # TODO: Determine if styles parameter should be used for grid customization
    def _style_grid(self, ax: Any, styles: dict[str, Any]) -> None:  # noqa: ARG002
        apply_grid_styling(ax, self.styler)
