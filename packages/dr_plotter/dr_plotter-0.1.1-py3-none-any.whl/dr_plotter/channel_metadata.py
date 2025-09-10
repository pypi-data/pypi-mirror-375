from dataclasses import dataclass
from typing import Literal


@dataclass
class ChannelSpec:
    name: str
    channel_type: Literal["categorical", "continuous"]
    legend_behavior: Literal["per_value", "min_max", "none"]


CHANNEL_SPECS = {
    "hue": ChannelSpec("hue", "categorical", "per_value"),
    "style": ChannelSpec("style", "categorical", "per_value"),
    "marker": ChannelSpec("marker", "categorical", "per_value"),
    "size": ChannelSpec("size", "categorical", "per_value"),
    "alpha": ChannelSpec("alpha", "categorical", "per_value"),
}


class ChannelRegistry:
    @staticmethod
    def get_spec(channel_name: str) -> ChannelSpec:
        return CHANNEL_SPECS.get(
            channel_name, ChannelSpec(channel_name, "categorical", "per_value")
        )

    @staticmethod
    def is_continuous(channel_name: str) -> bool:
        return ChannelRegistry.get_spec(channel_name).channel_type == "continuous"

    @staticmethod
    def get_legend_behavior(channel_name: str) -> str:
        return ChannelRegistry.get_spec(channel_name).legend_behavior
