from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from dr_plotter.types import ColName, VisualChannel


@dataclass
class GroupingConfig:
    hue: ColName | None = None
    style: ColName | None = None
    size: ColName | None = None
    marker: ColName | None = None
    alpha: ColName | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        pass

    @property
    def active_channels(self) -> set[VisualChannel]:
        return {
            field.name
            for field in fields(self)
            if getattr(self, field.name) is not None
        }

    @property
    def active_channels_ordered(self) -> list[VisualChannel]:
        return sorted(self.active_channels)

    @property
    def active(self) -> dict[VisualChannel, ColName]:
        return {
            channel: getattr(self, channel) for channel in self.active_channels_ordered
        }

    def set_kwargs(self, kwargs: dict[str, Any]) -> None:
        for field in fields(self):
            col_name = kwargs.get(f"{field.name}_by")
            if col_name is not None:
                setattr(self, field.name, col_name)

    def validate_against_enabled(self, enabled_channels: set[VisualChannel]) -> None:
        unsupported = self.active_channels - enabled_channels
        assert len(unsupported) == 0, f"Unsupported groupings: {unsupported}"

    @classmethod
    def get_grouping_param_names(cls) -> set[str]:
        """Get all possible grouping parameter names (e.g., 'hue_by', 'alpha_by')."""
        return {f"{field.name}_by" for field in fields(cls)}

    @classmethod
    def from_input(
        cls, value: dict[str, Any] | GroupingConfig | None
    ) -> GroupingConfig:
        if value is None:
            return cls()
        elif isinstance(value, cls):
            return value
        elif isinstance(value, dict):
            resolved_kwargs = {}
            for field in fields(cls):
                by_key = f"{field.name}_by"
                if by_key in value:
                    resolved_kwargs[field.name] = value[by_key]
            return cls(**resolved_kwargs)
        else:
            raise TypeError(f"Cannot create GroupingConfig from {type(value).__name__}")
