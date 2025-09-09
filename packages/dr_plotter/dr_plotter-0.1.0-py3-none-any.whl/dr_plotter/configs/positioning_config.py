from dataclasses import dataclass


@dataclass
class PositioningConfig:
    default_margin_bottom: float = 0.15
    default_margin_top: float = 0.95
    default_margin_left: float = 0.0
    default_margin_right: float = 1.0

    legend_y_offset_factor: float = 0.08
    legend_spacing_base: float = 0.35
    legend_alignment_center: float = 0.5

    two_legend_positions: tuple[float, float] = (0.25, 0.75)
    multi_legend_start_factor: float = 0.15

    title_space_factor: float = 0.95
    tight_layout_pad: float = 0.5

    wide_figure_threshold: float = 16.0
    medium_figure_threshold: float = 12.0
    wide_spacing_max: float = 0.35
    medium_spacing_max: float = 0.3
    wide_span_factor: float = 0.8
    medium_span_factor: float = 0.7

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        pass
