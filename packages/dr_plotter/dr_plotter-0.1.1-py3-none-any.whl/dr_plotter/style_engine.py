from __future__ import annotations
from typing import Any

from dr_plotter.channel_metadata import ChannelRegistry
from dr_plotter.configs import CycleConfig, GroupingConfig
from dr_plotter.theme import Theme


class StyleEngine:
    def __init__(self, theme: Theme, figure_manager: Any | None = None) -> None:
        self.theme = theme
        self.figure_manager = figure_manager
        self._local_cycle_config = CycleConfig(theme)
        self._continuous_ranges: dict[str, dict[str, float]] = {}

    @property
    def cycle_cfg(self) -> CycleConfig:
        if self.figure_manager and self.figure_manager.shared_cycle_config:
            return self.figure_manager.shared_cycle_config
        return self._local_cycle_config

    def set_continuous_range(
        self, channel: str, column: str, values: list[float]
    ) -> None:
        if not values:
            return
        key = f"{channel}:{column}"
        min_val = float(min(values))
        max_val = float(max(values))
        range_val = max_val - min_val
        self._continuous_ranges[key] = {
            "min": min_val,
            "max": max_val,
            "range": range_val,
        }

    def get_styles_for_group(
        self, group_values: dict[str, Any], grouping_cfg: GroupingConfig
    ) -> dict[str, Any]:
        styles = {}
        for channel, column in grouping_cfg.active.items():
            value = group_values.get(column)
            if value is not None:
                spec = ChannelRegistry.get_spec(channel)
                if spec.channel_type == "continuous":
                    continuous_styles = self.get_continuous_style(
                        channel, column, value
                    )
                    if continuous_styles:
                        styles.update(continuous_styles)
                    else:
                        styles.update(
                            self.cycle_cfg.get_styled_value_for_channel(channel, value)
                        )
                else:
                    styles.update(
                        self.cycle_cfg.get_styled_value_for_channel(channel, value)
                    )
        return styles

    def get_continuous_style(
        self, channel: str, column: str, value: float
    ) -> dict[str, Any]:
        key = f"{channel}:{column}"
        if key not in self._continuous_ranges:
            return {"size_mult": 1.0} if channel == "size" else {}

        range_info = self._continuous_ranges[key]
        if range_info["range"] == 0:
            normalized = 0.5
        else:
            normalized = (float(value) - range_info["min"]) / range_info["range"]

        if channel == "size":
            size_mult = 0.5 + normalized * 2.5
            return {"size_mult": size_mult}
        elif channel == "alpha":
            alpha_min = self.theme.get("alpha_min", 0.3)
            alpha_max = self.theme.get("alpha_max", 1.0)
            alpha = alpha_min + normalized * (alpha_max - alpha_min)
            return {"alpha": alpha}

        return {}
