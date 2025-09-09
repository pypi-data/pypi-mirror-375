from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dr_plotter.theme import (
    BAR_THEME,
    BASE_THEME,
    BUMP_PLOT_THEME,
    CONTOUR_THEME,
    GROUPED_BAR_THEME,
    HEATMAP_THEME,
    HISTOGRAM_THEME,
    LINE_THEME,
    SCATTER_THEME,
    VIOLIN_THEME,
    Theme,
)
from dr_plotter.types import ColorPalette

DEFAULT_THEME_STR = "base"
THEME_MAP = {
    "base": BASE_THEME,
    "line": LINE_THEME,
    "scatter": SCATTER_THEME,
    "bar": BAR_THEME,
    "histogram": HISTOGRAM_THEME,
    "violin": VIOLIN_THEME,
    "heatmap": HEATMAP_THEME,
    "bump": BUMP_PLOT_THEME,
    "contour": CONTOUR_THEME,
    "grouped_bar": GROUPED_BAR_THEME,
}


@dataclass
class StyleConfig:
    shared_styling: bool = True

    colors: ColorPalette | None = None
    plot_styles: dict[str, Any] | None = field(default_factory=dict)
    fonts: dict[str, Any] | None = field(default_factory=dict)
    figure_styles: dict[str, Any] | None = field(default_factory=dict)
    theme: str | Theme | None = None

    def __post_init__(self) -> None:
        self.validate()
        self._resolve_and_set_theme()

    def validate(self) -> None:
        assert (
            self.theme is None
            or (isinstance(self.theme, str) and self.theme in THEME_MAP)
            or isinstance(self.theme, Theme)
        ), "Theme must be None, a valid string in THEME_MAP, or a Theme object"

    def _resolve_and_set_theme(self) -> None:
        if isinstance(self.theme, Theme):
            return
        self.theme = THEME_MAP[DEFAULT_THEME_STR if self.theme is None else self.theme]

    @classmethod
    def from_input(
        cls, value: str | dict[str, Any] | StyleConfig | None
    ) -> StyleConfig:
        if value is None:
            return cls()
        elif isinstance(value, cls):
            return value
        elif isinstance(value, str):
            return cls(theme=value)
        elif isinstance(value, dict):
            return cls(**value)
        else:
            raise TypeError(f"Cannot create StyleConfig from {type(value).__name__}")
