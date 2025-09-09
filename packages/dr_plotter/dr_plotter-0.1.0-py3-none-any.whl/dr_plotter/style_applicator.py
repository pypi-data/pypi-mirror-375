from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from dr_plotter.configs import GroupingConfig
from dr_plotter.consts import VISUAL_CHANNELS
from dr_plotter.legend_manager import LegendEntry, LegendStrategy
from dr_plotter.theme import (
    BAR_THEME,
    BUMP_PLOT_THEME,
    CONTOUR_THEME,
    HEATMAP_THEME,
    HISTOGRAM_THEME,
    LINE_THEME,
    SCATTER_THEME,
    VIOLIN_THEME,
    Theme,
)
from dr_plotter.types import ComponentSchema, ComponentStyles, Phase

if TYPE_CHECKING:
    from dr_plotter.style_engine import StyleEngine


class StyleApplicator:
    def __init__(
        self,
        theme: Theme,
        kwargs: dict[str, Any],
        grouping_cfg: GroupingConfig | None = None,
        group_values: dict[str, Any] | None = None,
        figure_manager: Any | None = None,
        plot_type: str | None = None,
        style_engine: StyleEngine | None = None,
    ) -> None:
        self.theme = theme
        self.kwargs = kwargs
        self.grouping_cfg = grouping_cfg
        self.group_values = group_values or {}
        self.figure_manager = figure_manager
        self.plot_type = plot_type
        self.style_engine = style_engine
        self._component_schemas = self._load_component_schemas()
        self._post_processors: dict[str, Callable] = {}

    def get_component_styles(
        self, plot_type: str, phase: Phase = "plot"
    ) -> ComponentStyles:
        schema = self._get_component_schema(plot_type, phase)
        component_styles = {}

        for component_name, component_attrs in schema.items():
            styles = self._resolve_component_styles(
                plot_type, component_name, component_attrs, phase
            )
            component_styles[component_name] = styles

        return component_styles

    def get_single_component_styles(
        self, plot_type: str, component: str, phase: Phase = "plot"
    ) -> dict[str, Any]:
        schema = self._get_component_schema(plot_type, phase)
        if component not in schema:
            return {}

        return self._resolve_component_styles(
            plot_type, component, schema[component], phase
        )

    def register_post_processor(
        self, plot_type: str, component: str, processor: Callable
    ) -> None:
        key = f"{plot_type}.{component}"
        self._post_processors[key] = processor

    def set_group_context(self, group_values: dict[str, Any]) -> None:
        self.group_values = group_values if group_values is not None else {}

    def clear_group_context(self) -> None:
        self.group_values = {}

    def apply_post_processing(self, plot_type: str, artists: dict[str, Any]) -> None:
        axes_styles = self.get_component_styles(plot_type, phase="axes")

        for component, styles in axes_styles.items():
            processor_key = f"{plot_type}.{component}"
            if processor_key in self._post_processors:
                processor = self._post_processors[processor_key]
                if component in artists:
                    processor(artists[component], styles)

    def create_legend_entry(
        self,
        artist: Any,
        label: str,
        axis: Any = None,
        artist_type: str = "main",
        explicit_channel: str | None = None,
    ) -> LegendEntry | None:
        if not label:
            return None

        if explicit_channel:
            channel = explicit_channel
            column_name = (
                getattr(self.grouping_cfg, channel, None) if self.grouping_cfg else None
            )
            channel_value = self.group_values.get(column_name) if column_name else None
            source_column = self.kwargs.get(f"{channel}_by") if channel else None

            if self._should_use_split_legend_label():
                label = str(channel_value) if channel_value is not None else label

        else:
            channel = None
            source_column = None
            if self.grouping_cfg and self.grouping_cfg.active_channels:
                channel = (
                    self.grouping_cfg.active_channels_ordered[0]
                    if self.grouping_cfg.active_channels
                    else None
                )
                source_column = self.kwargs.get(f"{channel}_by") if channel else None
            channel_value = self.group_values.get(channel) if channel else None

        return LegendEntry(
            artist=artist,
            label=label,
            axis=axis,
            visual_channel=channel,
            channel_value=channel_value,
            source_column=source_column,
            group_key=self.group_values.copy(),
            plotter_type=self.plot_type or "unknown",
            artist_type=artist_type,
        )

    def get_style(self, key: str, default: Any = None) -> Any:
        """
        Get style with enhanced fallback resolution.
        Priority: kwargs → theme → default
        """
        return self.kwargs.get(key, self.theme.get(key, default))

    def get_computed_style(self, base_key: str, operation: str, factor: float) -> Any:
        """
        Get computed style value (e.g., size multiplication).
        """
        base_value = self.get_style(base_key, 1.0 if "size" in base_key else 0.0)

        if operation == "multiply":
            return base_value * factor
        elif operation == "add":
            return base_value + factor
        else:
            raise ValueError(f"Unsupported computation operation: {operation}")

    def _resolve_component_styles(
        self, plot_type: str, component: str, attrs: set[str], phase: Phase = "plot"
    ) -> dict[str, Any]:
        base_styles = self._get_base_theme_styles(phase)
        plot_styles = self._get_plot_specific_theme_styles(plot_type, phase)
        group_styles = self._get_group_styles_for_component(plot_type, component)
        component_kwargs = self._extract_component_kwargs(component, attrs)

        return self._merge_style_precedence(
            base_styles,
            plot_styles,
            group_styles,
            component_kwargs,
            attrs,
            plot_type,
            component,
        )

    def _get_base_theme_styles(self, phase: Phase) -> dict[str, Any]:
        base_styles = {}
        base_styles.update(self.theme.general_styles)

        if phase == "plot":
            base_styles.update(self.theme.plot_styles)
        elif phase == "post":
            base_styles.update(self.theme.post_styles)
        elif phase == "axes":
            base_styles.update(self.theme.axes_styles)
        elif phase == "figure":
            base_styles.update(self.theme.figure_styles)

        return base_styles

    def _get_plot_specific_theme_styles(
        self, plot_type: str, phase: Phase
    ) -> dict[str, Any]:
        plot_styles = {}
        plot_specific_themes = self._get_plot_specific_themes()

        if plot_type not in plot_specific_themes:
            return plot_styles

        plot_theme = plot_specific_themes[plot_type]
        plot_styles.update(plot_theme.general_styles)

        if phase == "plot":
            plot_styles.update(plot_theme.plot_styles)
        elif phase == "post":
            plot_styles.update(plot_theme.post_styles)
        elif phase == "axes":
            plot_styles.update(plot_theme.axes_styles)
        elif phase == "figure":
            plot_styles.update(plot_theme.figure_styles)

        return plot_styles

    def _resolve_default_attribute(
        self,
        attr: str,
        plot_type: str,
        component: str,
        base_styles: dict[str, Any],
        group_styles: dict[str, Any],
    ) -> Any:
        if attr == "s" and "size_mult" in group_styles and plot_type == "scatter":
            base_size = base_styles.get("marker_size", 50)
            return base_size * group_styles["size_mult"]

        if attr == "color":
            if component == "main":
                return base_styles["default_color"]
            else:
                return base_styles["text_color"]

        if attr == "fontsize":
            return base_styles["text_fontsize"]
        elif attr == "ha":
            return base_styles["text_ha"]
        elif attr == "va":
            return base_styles["text_va"]

        return None

    def _merge_style_precedence(
        self,
        base_styles: dict[str, Any],
        plot_styles: dict[str, Any],
        group_styles: dict[str, Any],
        component_kwargs: dict[str, Any],
        attrs: set[str],
        plot_type: str,
        component: str,
    ) -> dict[str, Any]:
        resolved_styles = {}

        for attr in attrs:
            if attr in component_kwargs:
                resolved_styles[attr] = component_kwargs[attr]
            elif attr in group_styles:
                resolved_styles[attr] = group_styles[attr]
            elif attr in plot_styles:
                resolved_styles[attr] = plot_styles[attr]
            elif attr in base_styles:
                resolved_styles[attr] = base_styles[attr]
            else:
                default_value = self._resolve_default_attribute(
                    attr, plot_type, component, base_styles, group_styles
                )
                if default_value is not None:
                    resolved_styles[attr] = default_value

        resolved_styles.update(
            {key: val for key, val in component_kwargs.items() if key not in attrs}
        )
        if "cmap" in resolved_styles and "c" not in resolved_styles:
            del resolved_styles["cmap"]

        return resolved_styles

    def _should_use_split_legend_label(self) -> bool:
        return (
            self.figure_manager
            and hasattr(self.figure_manager, "legend_config")
            and self.figure_manager.legend_config.strategy
            == LegendStrategy.GROUPED_BY_CHANNEL
        )

    def _extract_component_kwargs(
        self, component: str, attrs: set[str]
    ) -> dict[str, Any]:
        if component == "main":
            return self._extract_main_component_kwargs(attrs)
        else:
            return self._extract_prefixed_component_kwargs(component, attrs)

    def _extract_main_component_kwargs(self, attrs: set[str]) -> dict[str, Any]:
        axes_specific = {"title", "xlabel", "ylabel", "grid"}
        axes_prefixed = {
            k
            for k in self.kwargs
            if any(k.startswith(f"{axis}_") for axis in axes_specific)
        }

        def extract_k_why_unknown(k: str) -> bool:
            if self._is_reserved_kwarg(k):
                return False
            if k in attrs:
                return True
            return (
                not k.endswith("_by")
                and k not in axes_specific
                and k not in axes_prefixed
            )

        extracted = {k: v for k, v in self.kwargs.items() if extract_k_why_unknown(k)}
        return extracted

    def _extract_prefixed_component_kwargs(
        self, component: str, attrs: set[str]
    ) -> dict[str, Any]:
        component_prefix = f"{component}_"
        extracted = {}

        for key, value in self.kwargs.items():
            if key.startswith(component_prefix):
                clean_key = key[len(component_prefix) :]
                extracted[clean_key] = value
            elif key in attrs and not any(
                key.startswith(f"{other}_")
                for other in ["contour", "scatter", "violin", "text", "line"]
            ):
                extracted[key] = value

        if component == "cell_text" and "display_values" in self.kwargs:
            extracted["visible"] = self.kwargs["display_values"]

        return extracted

    def _is_reserved_kwarg(self, key: str) -> bool:
        visual_channel_names = set(VISUAL_CHANNELS)
        visual_channel_by_names = {f"{ch}_by" for ch in VISUAL_CHANNELS}
        reserved = {
            "x",
            "y",
            "data",
            "theme",
            "legend",
            "colorbar_label",
            "time_col",
            "category_col",
            "value_col",
            "grouping_cfg",
        }
        reserved.update(visual_channel_by_names)

        if key in visual_channel_names and key in self.kwargs:
            value = self.kwargs[key]
            return bool(isinstance(value, str))

        return key in reserved

    def _get_group_styles_for_component(
        self,
        plot_type: str,
        component: str,
    ) -> dict[str, Any]:
        if not self.grouping_cfg or not self.group_values:
            return {}

        group_styled_components = self._get_group_styled_components(plot_type)
        if component not in group_styled_components:
            return {}

        if not self.style_engine:
            from dr_plotter.style_engine import StyleEngine

            self.style_engine = StyleEngine(self.theme, self.figure_manager)

        return self.style_engine.get_styles_for_group(
            self.group_values, self.grouping_cfg
        )

    def _get_component_schema(
        self, plot_type: str, phase: Phase = "plot"
    ) -> ComponentSchema:
        from dr_plotter.plotters.base import BasePlotter

        plotter_cls = BasePlotter.get_plotter(plot_type)
        if plotter_cls and hasattr(plotter_cls, "component_schema"):
            return plotter_cls.component_schema.get(phase, {})

        plot_schemas = self._component_schemas.get(plot_type, {})
        if isinstance(plot_schemas, dict) and phase in plot_schemas:
            return plot_schemas[phase]
        elif (
            phase == "plot"
            and isinstance(plot_schemas, dict)
            and "plot" not in plot_schemas
            and "main" in plot_schemas
        ):
            return plot_schemas
        return {"main": set()}

    def _get_group_styled_components(self, plot_type: str) -> set[str]:
        group_styled_map = {
            "scatter": {"main"},
            "line": {"main"},
            "bar": {"main"},
            "histogram": {"main"},
            "violin": {"bodies"},
            "heatmap": {"main"},
            "contour": {"scatter"},
            "bump": {"line"},
        }
        return group_styled_map.get(plot_type, {"main"})

    def _get_plot_specific_themes(self) -> dict[str, Theme]:
        return {
            "line": LINE_THEME,
            "scatter": SCATTER_THEME,
            "bar": BAR_THEME,
            "histogram": HISTOGRAM_THEME,
            "violin": VIOLIN_THEME,
            "heatmap": HEATMAP_THEME,
            "bump": BUMP_PLOT_THEME,
            "contour": CONTOUR_THEME,
        }

    def _load_component_schemas(self) -> dict[str, dict[Phase, ComponentSchema]]:
        return {}
