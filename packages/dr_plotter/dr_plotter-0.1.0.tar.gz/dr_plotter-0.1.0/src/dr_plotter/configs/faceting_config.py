from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FacetingConfig:
    rows: str | None = None
    cols: str | None = None
    lines: str | None = None

    row_order: list[str] | None = None
    col_order: list[str] | None = None
    lines_order: list[str] | None = None

    x: str | None = None
    y: str | None = None

    x_labels: list[list[str | None]] | None = None
    y_labels: list[list[str | None]] | None = None
    xlim: list[list[tuple[float, float] | None]] | None = None
    ylim: list[list[tuple[float, float] | None]] | None = None

    subplot_titles: str | list[list[str | None]] | None = None
    title_template: str | None = None

    color_wrap: bool = False

    row_titles: bool | list[str] | None = None
    col_titles: bool | list[str] | None = None

    exterior_x_label: str | None = None
    exterior_y_label: str | None = None

    target_row: int | None = None
    target_col: int | None = None

    target_positions: dict[tuple[int, int], tuple[int, int]] | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not (self.rows or self.cols):
            assert False, "Facet by rows or cols (eg rows='data')"
