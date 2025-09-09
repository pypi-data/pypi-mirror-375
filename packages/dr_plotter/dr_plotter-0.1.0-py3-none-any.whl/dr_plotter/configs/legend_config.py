from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from dr_plotter.configs.positioning_config import PositioningConfig


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
    strategy: str = "subplot"
    collect_strategy: str = "smart"
    position: str = "lower center"
    deduplication: bool = True
    ncol: int | None = None
    max_col: int = 4
    spacing: float = 0.1
    remove_axes_legends: bool = True
    channel_titles: dict[str, str] | None = None
    layout_left_margin: float = 0.0
    layout_bottom_margin: float = 0.15
    layout_right_margin: float = 1.0
    layout_top_margin: float = 0.95
    positioning_config: PositioningConfig | None = None

    def __post_init__(self) -> None:
        self.validate()
        self.strategy = SHORT_NAME_STRATEGY_MAP[self.strategy]
        if self.positioning_config is None:
            self.positioning_config = PositioningConfig()

    def validate(self) -> None:
        assert self.strategy in SHORT_NAME_STRATEGY_MAP, (
            f"Invalid legend strategy '{self.strategy}'. Valid options: "
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
