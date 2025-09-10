from __future__ import annotations
from typing import Any
import pandas as pd

DEFAULT_COLOR_CYCLE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

DEFAULT_MARKER_CYCLE = ["o", "s", "^", "D", "v", "<", ">", "p", "*", "h"]


class FacetStyleCoordinator:
    def __init__(self, theme: dict[str, Any] | None = None) -> None:
        self._style_assignments: dict[str, dict[Any, dict[str, Any]]] = {}
        self._color_cycle = _get_theme_colors(theme)
        self._marker_cycle = _get_theme_markers(theme)
        self._next_color_index = 0

    def register_dimension_values(self, dimension: str, values: list[Any]) -> None:
        assert dimension, "Dimension name cannot be empty"
        assert values, "Values list cannot be empty"

        if dimension not in self._style_assignments:
            self._style_assignments[dimension] = {}

        for value in values:
            if value not in self._style_assignments[dimension]:
                self._assign_style_to_value(dimension, value)

    def _assign_style_to_value(self, dimension: str, value: Any) -> None:
        color_idx = self._next_color_index % len(self._color_cycle)
        marker_idx = self._next_color_index % len(self._marker_cycle)

        self._style_assignments[dimension][value] = {
            "color": self._color_cycle[color_idx],
            "marker": self._marker_cycle[marker_idx],
        }
        self._next_color_index += 1

    def get_consistent_style(self, dimension: str, value: Any) -> dict[str, Any]:
        assert dimension, "Dimension name cannot be empty"

        if dimension not in self._style_assignments:
            self._style_assignments[dimension] = {}

        if value not in self._style_assignments[dimension]:
            self._assign_style_to_value(dimension, value)

        return self._style_assignments[dimension][value].copy()

    # TODO: Consider if row/col parameters are needed for future subplot styling
    def get_subplot_styles(
        self,
        row: int,  # noqa: ARG002
        col: int,  # noqa: ARG002
        dimension: str | None,
        subplot_data: pd.DataFrame,
        **plot_kwargs: Any,
    ) -> dict[str, Any]:
        if dimension is None or dimension not in subplot_data.columns:
            return plot_kwargs

        dimension_values = subplot_data[dimension].unique()

        if len(dimension_values) == 1:
            value = dimension_values[0]
            style = self.get_consistent_style(dimension, value)
            result_kwargs = plot_kwargs.copy()
            result_kwargs.update(style)
            return result_kwargs

        return plot_kwargs


def _get_theme_colors(theme: dict[str, Any] | None) -> list[str]:
    if theme and "color_cycle" in theme:
        return theme["color_cycle"]
    return DEFAULT_COLOR_CYCLE


def _get_theme_markers(theme: dict[str, Any] | None) -> list[str]:
    if theme and "marker_cycle" in theme:
        return theme["marker_cycle"]
    return DEFAULT_MARKER_CYCLE
