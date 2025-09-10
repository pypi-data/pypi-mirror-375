from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

# Removed PositioningConfig import - using simple coordinates now


class LegendStrategy(Enum):
    PER_AXES = "per_axes"
    FIGURE_BELOW = "figure_below"
    GROUPED_BY_CHANNEL = "grouped_by_channel"
    NONE = "none"


SHORT_NAME_STRATEGY_MAP = {
    "grouped": LegendStrategy.GROUPED_BY_CHANNEL,
    "subplot": LegendStrategy.PER_AXES,
    "figure": LegendStrategy.FIGURE_BELOW,
    "none": LegendStrategy.NONE,
}


@dataclass
class LegendConfig:
    legend_strategy: str = "subplot"
    collect_strategy: str = "smart"
    position: str = "lower center"
    deduplication: bool = True
    ncol: int | None = None
    max_col: int = 4
    spacing: float = 0.1
    remove_axes_legends: bool = True
    channel_titles: dict[str, str] | None = None
    legend_position: tuple[float, float] | None = (
        None  # (x, y) coordinates, uses theme default if None
    )
    multi_legend_positions: list[tuple[float, float]] | None = (
        None  # For multi-legend cases
    )

    def __post_init__(self) -> None:
        self.validate()
        self.legend_strategy = SHORT_NAME_STRATEGY_MAP[self.legend_strategy]

    def validate(self) -> None:
        assert self.legend_strategy in SHORT_NAME_STRATEGY_MAP, (
            f"Invalid legend strategy '{self.legend_strategy}'. Valid options: "
            f"{list(SHORT_NAME_STRATEGY_MAP.keys())}"
        )

    @classmethod
    def from_input(
        cls, value: str | dict[str, Any] | LegendConfig | None
    ) -> LegendConfig:
        if value is None:
            return cls()
        elif isinstance(value, cls):
            return value
        elif isinstance(value, str):
            from dr_plotter.legend_manager import resolve_legend_config

            return resolve_legend_config(value)
        elif isinstance(value, dict):
            legend_kwargs = {}
            for key, val in value.items():
                if key == "style":
                    legend_kwargs["strategy"] = val
                else:
                    legend_kwargs[key] = val
            return cls(**legend_kwargs)
        else:
            raise TypeError(f"Cannot create LegendConfig from {type(value).__name__}")
