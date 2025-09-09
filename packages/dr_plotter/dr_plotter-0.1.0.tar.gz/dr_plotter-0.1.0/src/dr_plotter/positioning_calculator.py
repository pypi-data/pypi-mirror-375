from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dr_plotter.configs.positioning_config import PositioningConfig


@dataclass
class FigureDimensions:
    width: float
    height: float
    rows: int
    cols: int
    has_title: bool = False
    has_subplot_titles: bool = False


@dataclass
class LegendMetadata:
    num_legends: int
    num_handles_per_legend: int
    has_titles: bool = False
    strategy: str = "figure_below"


@dataclass
class PositioningResult:
    legend_positions: dict[int, tuple[float, float]]
    layout_rect: tuple[float, float, float, float] | None = None
    tight_layout_pad: float = 0.5
    margin_adjustments: dict[str, float] | None = None


class PositioningCalculator:
    def __init__(self, config: PositioningConfig | None = None) -> None:
        self.config = config or PositioningConfig()

    def calculate_positions(
        self,
        figure_dimensions: FigureDimensions,
        legend_metadata: LegendMetadata,
        manual_overrides: dict[str, Any] | None = None,
    ) -> PositioningResult:
        return self._resolve_positioning_hierarchy(
            figure_dimensions, legend_metadata, manual_overrides or {}
        )

    def _resolve_positioning_hierarchy(
        self,
        figure_dimensions: FigureDimensions,
        legend_metadata: LegendMetadata,
        manual_overrides: dict[str, Any],
    ) -> PositioningResult:
        if "bbox_to_anchor" in manual_overrides:
            return self._handle_manual_positioning(manual_overrides, figure_dimensions)

        if legend_metadata.strategy in ["grouped_by_channel", "figure_below"]:
            return self._calculate_figure_legend_positions(
                figure_dimensions, legend_metadata, manual_overrides
            )

        return self._calculate_default_positioning(figure_dimensions)

    def _handle_manual_positioning(
        self, manual_overrides: dict[str, Any], figure_dimensions: FigureDimensions
    ) -> PositioningResult:
        bbox = manual_overrides["bbox_to_anchor"]
        return PositioningResult(
            legend_positions={0: bbox},
            layout_rect=self._calculate_layout_rect(figure_dimensions),
            tight_layout_pad=self.config.tight_layout_pad,
        )

    # TODO: Implement manual positioning overrides for legend placement
    def _calculate_figure_legend_positions(
        self,
        figure_dimensions: FigureDimensions,
        legend_metadata: LegendMetadata,
        manual_overrides: dict[str, Any],  # noqa: ARG002
    ) -> PositioningResult:
        num_legends = legend_metadata.num_legends

        positions = {}
        for legend_index in range(num_legends):
            x, y = self._calculate_systematic_position(
                num_legends, legend_index, figure_dimensions.width
            )
            positions[legend_index] = (x, y)

        layout_rect = self._calculate_layout_rect_with_legends()

        return PositioningResult(
            legend_positions=positions,
            layout_rect=layout_rect,
            tight_layout_pad=self.config.tight_layout_pad,
            margin_adjustments={
                "bottom": self.config.default_margin_bottom,
                "top": self.config.default_margin_top,
            },
        )

    def _calculate_systematic_position(
        self, num_legends: int, legend_index: int, figure_width: float
    ) -> tuple[float, float]:
        pos_configs = {
            1: self.config.legend_alignment_center,
            2: self.config.two_legend_positions[legend_index],
        }
        y_position = self.config.legend_y_offset_factor
        if num_legends > 0 and num_legends <= max(pos_configs.keys()):
            return (pos_configs[num_legends], y_position)

        spacing, start_x = self._calculate_multi_legend_layout(
            num_legends, figure_width
        )
        x_position = start_x + (legend_index * spacing)

        return (x_position, y_position)

    def _calculate_multi_legend_layout(
        self, num_legends: int, figure_width: float
    ) -> tuple[float, float]:
        if figure_width >= self.config.wide_figure_threshold:
            max_spacing = self.config.wide_spacing_max
            span_factor = self.config.wide_span_factor
        elif figure_width >= self.config.medium_figure_threshold:
            max_spacing = self.config.medium_spacing_max
            span_factor = self.config.medium_span_factor
        else:
            return (
                self.config.legend_spacing_base,
                self.config.multi_legend_start_factor,
            )

        optimal_spacing = min(max_spacing, span_factor / (num_legends - 1))
        start_x = (
            self.config.legend_alignment_center
            - (num_legends - 1) * optimal_spacing / 2
        )

        return (optimal_spacing, start_x)

    def calculate_layout_rect(
        self, figure_dimensions: FigureDimensions
    ) -> tuple[float, float, float, float] | None:
        return self._calculate_layout_rect(figure_dimensions)

    def _calculate_layout_rect(
        self, figure_dimensions: FigureDimensions
    ) -> tuple[float, float, float, float] | None:
        if figure_dimensions.has_title or figure_dimensions.has_subplot_titles:
            return (0.0, 0.0, 1.0, self.config.title_space_factor)
        return None

    def _calculate_layout_rect_with_legends(self) -> tuple[float, float, float, float]:
        return (
            self.config.default_margin_left,
            self.config.default_margin_bottom,
            self.config.default_margin_right,
            self.config.default_margin_top,
        )

    def _calculate_default_positioning(
        self, figure_dimensions: FigureDimensions
    ) -> PositioningResult:
        positions = {
            0: (
                self.config.legend_alignment_center,
                self.config.legend_y_offset_factor,
            )
        }

        return PositioningResult(
            legend_positions=positions,
            layout_rect=self._calculate_layout_rect(figure_dimensions),
            tight_layout_pad=self.config.tight_layout_pad,
        )
