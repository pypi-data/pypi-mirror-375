from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dr_plotter.configs.layout_config import LayoutConfig
from dr_plotter.configs.legend_config import LegendConfig
from dr_plotter.configs.style_config import StyleConfig
from dr_plotter.plot_presets import PLOT_CONFIGS


@dataclass
class PlotConfig:
    layout: tuple[int, int] | dict[str, Any] | LayoutConfig | None = None
    style: str | dict[str, Any] | StyleConfig | None = None
    legend: str | dict[str, Any] | LegendConfig | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.validate()
        self.layout = LayoutConfig.from_input(self.layout)
        self.style = StyleConfig.from_input(self.style)
        self.legend = LegendConfig.from_input(self.legend)

    def validate(self) -> None:
        pass

    @classmethod
    def from_preset(cls, preset_name: str) -> PlotConfig:
        assert preset_name in PLOT_CONFIGS, (
            f"Unknown preset: {preset_name}. Available: {list(PLOT_CONFIGS.keys())}"
        )

        preset_config = PLOT_CONFIGS[preset_name]
        return cls(**preset_config)
