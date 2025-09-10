from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FacetingConfig:
    x: str | None = None
    y: str | None = None

    rows_by: str | None = None
    cols_by: str | None = None
    wrap_by: str | None = None
    max_cols: int | None = None
    max_rows: int | None = None

    hue_by: str | None = None
    alpha_by: str | None = None
    size_by: str | None = None
    marker_by: str | None = None
    style_by: str | None = None

    fixed: dict[str, str] | None = None
    order: dict[str, list[str]] | None = None
    exclude: dict[str, list[str]] | None = None

    subplot_width: float | None = None
    subplot_height: float | None = None
    auto_titles: bool = True

    subplot_titles: str | list[list[str | None]] | None = None
    title_template: str | None = None

    color_wrap: bool = False

    row_titles: bool | list[str] | None = None
    col_titles: bool | list[str] | None = None
    row_title_rotation: float | None = None
    row_title_offset: float | None = None

    exterior_x_label: str | None = None
    exterior_y_label: str | None = None

    target_row: int | None = None
    target_col: int | None = None

    target_positions: dict[tuple[int, int], tuple[int, int]] | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        assert self.x is not None, "x parameter is required for faceting"
        assert self.y is not None, "y parameter is required for faceting"

    @classmethod
    def from_input(
        cls, value: dict[str, Any] | FacetingConfig | None
    ) -> FacetingConfig | None:
        if value is None:
            return None
        elif isinstance(value, cls):
            return value
        elif isinstance(value, dict):
            return cls(**value)
        else:
            raise TypeError(f"Cannot create FacetingConfig from {type(value).__name__}")
