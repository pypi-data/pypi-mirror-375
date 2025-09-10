from __future__ import annotations

from typing import Any, ClassVar

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter import consts
from dr_plotter.configs import GroupingConfig
from dr_plotter.theme import LINE_THEME, Theme
from dr_plotter.types import ComponentSchema, Phase, VisualChannel

from .base import BasePlotter


class LinePlotter(BasePlotter):
    plotter_name: str = "line"
    plotter_params: ClassVar[list[str]] = []
    enabled_channels: ClassVar[set[VisualChannel]] = {
        "hue",
        "style",
        "size",
        "marker",
        "alpha",
    }
    default_theme: ClassVar[Theme] = LINE_THEME

    component_schema: ClassVar[dict[Phase, ComponentSchema]] = {
        "plot": {
            "main": {
                "color",
                "linestyle",
                "linewidth",
                "marker",
                "markersize",
                "alpha",
                "label",
            }
        },
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
        super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)
        self.styler.register_post_processor("line", "lines", self._style_lines)

    def _style_lines(self, lines: Any, styles: dict[str, Any]) -> None:
        for line in lines:
            for attr, value in styles.items():
                if attr == "color" and hasattr(line, "set_color"):
                    line.set_color(value)
                elif attr == "linewidth" and hasattr(line, "set_linewidth"):
                    line.set_linewidth(value)
                elif attr == "linestyle" and hasattr(line, "set_linestyle"):
                    line.set_linestyle(value)
                elif attr == "marker" and hasattr(line, "set_marker"):
                    line.set_marker(value)
                elif attr == "markersize" and hasattr(line, "set_markersize"):
                    line.set_markersize(value)
                elif attr == "alpha" and hasattr(line, "set_alpha"):
                    line.set_alpha(value)
                elif hasattr(line, f"set_{attr}"):
                    setter = getattr(line, f"set_{attr}")
                    setter(value)

    def _draw(self, ax: plt.Axes, data: pd.DataFrame, **kwargs: Any) -> None:
        label = kwargs.pop("label", None)
        data_sorted = data.sort_values(consts.X_COL_NAME)
        config = self._resolve_phase_config("main", data=data_sorted, **kwargs)

        lines = ax.plot(
            data_sorted[consts.X_COL_NAME], data_sorted[consts.Y_COL_NAME], **config
        )

        artists = {"lines": lines}
        self.styler.apply_post_processing("line", artists)

        self._apply_post_processing(lines, label)

    def _apply_post_processing(self, lines: Any, label: str | None = None) -> None:
        if not self._should_create_legend():
            self._apply_styling(self.current_axis)
            return

        if self.figure_manager and label and lines:
            line = lines[0] if isinstance(lines, list) else lines
            for channel in self.grouping_params.active_channels_ordered:
                entry = self.styler.create_legend_entry(
                    line, label, self.current_axis, explicit_channel=channel
                )
                if entry:
                    self.figure_manager.register_legend_entry(entry)

        self._apply_styling(self.current_axis)
