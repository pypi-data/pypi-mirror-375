from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dr_plotter.configs.legend_config import LegendConfig, LegendStrategy


@dataclass
class LegendEntry:
    artist: Any
    label: str
    axis: Any = None
    visual_channel: str | None = None
    channel_value: Any = None
    source_column: str | None = None
    group_key: dict[str, Any] = field(default_factory=dict)
    plotter_type: str = "unknown"
    artist_type: str = "main"


class LegendRegistry:
    def __init__(self, strategy: LegendStrategy | None = None) -> None:
        self._entries: list[LegendEntry] = []
        self._seen_keys: set[tuple] = set()
        self.legend_strategy = strategy

    def add_entry(self, entry: LegendEntry) -> None:
        if self._should_use_channel_based_deduplication():
            key = (entry.visual_channel, entry.channel_value)
        else:
            key = (entry.label, id(entry.axis))

        if key not in self._seen_keys:
            self._entries.append(entry)
            self._seen_keys.add(key)

    def _should_use_channel_based_deduplication(self) -> bool:
        if self.legend_strategy is None:
            return False
        shared_strategies = {
            LegendStrategy.GROUPED_BY_CHANNEL,
            LegendStrategy.FIGURE_BELOW,
        }
        return self.legend_strategy in shared_strategies

    def get_unique_entries(self) -> list[LegendEntry]:
        return self._entries.copy()

    def get_by_channel(self, channel: str) -> list[LegendEntry]:
        return [e for e in self._entries if e.visual_channel == channel]

    def clear(self) -> None:
        self._entries.clear()
        self._seen_keys.clear()


def resolve_legend_config(legend_input: str | LegendConfig) -> LegendConfig:
    if isinstance(legend_input, str):
        string_mappings = {
            "grouped": LegendConfig(strategy="grouped"),
            "subplot": LegendConfig(strategy="subplot"),
            "figure": LegendConfig(strategy="figure"),
            "none": LegendConfig(strategy="none"),
        }
        assert legend_input in string_mappings, (
            f"Invalid legend string '{legend_input}'. Valid options: "
            f"{list(string_mappings.keys())}"
        )
        return string_mappings[legend_input]
    return legend_input


class LegendManager:
    def __init__(self, figure_manager: Any, config: LegendConfig | None = None) -> None:
        self.fm = figure_manager
        self.config = config or LegendConfig()
        self.registry = LegendRegistry(self.config.legend_strategy)

    def _get_legend_position(self, legend_index: int = 0) -> tuple[float, float]:
        if self.config.legend_position is not None:
            return self.config.legend_position

        if self.config.multi_legend_positions is not None and legend_index < len(
            self.config.multi_legend_positions
        ):
            return self.config.multi_legend_positions[legend_index]

        if self.config.legend_strategy == LegendStrategy.GROUPED_BY_CHANNEL:
            multi_positions = self.fm.styler.get_style("multi_legend_positions")
            if multi_positions and legend_index < len(multi_positions):
                return multi_positions[legend_index]
            else:
                return (legend_index * 0.25 + 0.25, 0.05)
        else:
            return self.fm.styler.get_style("legend_position")

    def _calculate_ncol(self, num_handles: int) -> int:
        if self.config.ncol is not None:
            return self.config.ncol
        return min(self.config.max_col, num_handles)

    def _contextualize_column_name(self, column_name: str) -> str:
        if column_name.endswith("_by"):
            column_name = column_name[:-3]

        if "_" in column_name:
            words = column_name.split("_")
            return " ".join(word.capitalize() for word in words)

        return column_name.capitalize()

    def generate_channel_title(self, channel: str, entries: list[LegendEntry]) -> str:
        if self.config.channel_titles and channel in self.config.channel_titles:
            return self.config.channel_titles[channel]

        source_columns = [
            e.source_column for e in entries if e.source_column is not None
        ]
        if source_columns:
            unique_sources = list(set(source_columns))
            if len(unique_sources) == 1:
                return self._contextualize_column_name(unique_sources[0])

        return channel.title()

    def calculate_optimal_ncol(self, legend_entries: list[LegendEntry]) -> int:
        if self.config.ncol is not None:
            return self.config.ncol
        return len(legend_entries) if len(legend_entries) > 0 else 1

    def finalize(self) -> None:
        if self.config.legend_strategy == LegendStrategy.NONE:
            return

        if self.config.legend_strategy == LegendStrategy.FIGURE_BELOW:
            self._create_figure_legend()
        elif self.config.legend_strategy == LegendStrategy.GROUPED_BY_CHANNEL:
            self._create_grouped_legends()
        elif self.config.legend_strategy == LegendStrategy.PER_AXES:
            self._create_per_axes_legends()

    def _process_entries_by_channel_type(
        self, entries: list[LegendEntry]
    ) -> list[LegendEntry]:
        return entries

    def _prepare_legend_entries(
        self, entries: list[LegendEntry]
    ) -> tuple[list[Any], list[str], list[LegendEntry]] | None:
        if not entries:
            return None

        entries = self._process_entries_by_channel_type(entries)
        handles = [entry.artist for entry in entries]
        labels = [entry.label for entry in entries]
        return handles, labels, entries

    def _create_figure_legend(self) -> None:
        entries = self.registry.get_unique_entries()
        result = self._prepare_legend_entries(entries)
        if result is None:
            return

        handles, labels, entries = result

        if not hasattr(self.fm, "fig") or not self.fm.fig or not self.fm.fig.axes:
            return

        ncol = self._calculate_ncol(len(handles))
        bbox_to_anchor = self._get_legend_position(0)
        title = None
        if entries and entries[0].visual_channel:
            title = self.generate_channel_title(entries[0].visual_channel, entries)

        self.fm.fig.legend(
            handles,
            labels,
            title=title,
            loc=self.config.position,
            bbox_to_anchor=bbox_to_anchor,
            ncol=ncol,
            frameon=self.fm.styler.get_style("legend_frameon", default=True),
        )

        if self.config.remove_axes_legends:
            for ax in self.fm.fig.axes:
                legend = ax.get_legend()
                if legend:
                    legend.remove()

    def _create_per_axes_legends(self) -> None:
        entries = self.registry.get_unique_entries()
        result = self._prepare_legend_entries(entries)
        if result is None:
            return

        _, _, entries = result

        entries_by_axis = {}
        for entry in entries:
            axis = entry.axis
            if axis is not None:
                if axis not in entries_by_axis:
                    entries_by_axis[axis] = []
                entries_by_axis[axis].append(entry)

        for axis, axis_entries in entries_by_axis.items():
            if not axis_entries:
                continue

            handles = []
            labels = []
            for entry in axis_entries:
                if entry.artist:
                    handles.append(entry.artist)
                    labels.append(entry.label)

            if handles:
                legend_position = (
                    "best"
                    if self.config.position == "lower center"
                    else self.config.position
                )

                title = None
                if axis_entries and axis_entries[0].visual_channel:
                    title = self.generate_channel_title(
                        axis_entries[0].visual_channel, axis_entries
                    )

                axis.legend(handles, labels, loc=legend_position, title=title)

    def _create_grouped_legends(self) -> None:
        channels = set()
        for entry in self.registry.get_unique_entries():
            if entry.visual_channel:
                channels.add(entry.visual_channel)
        channel_list = sorted(channels)

        if self.config.legend_strategy == LegendStrategy.GROUPED_BY_CHANNEL:
            legends_to_create = [(i, channel) for i, channel in enumerate(channel_list)]
        elif self.config.legend_strategy == LegendStrategy.FIGURE_BELOW:
            legends_to_create = [(0, None)]
        else:
            return

        for legend_index, channel in legends_to_create:
            if channel is not None:
                entries = self.registry.get_by_channel(channel)
            else:
                entries = self.registry.get_unique_entries()

            result = self._prepare_legend_entries(entries)
            if result is None:
                continue

            handles, labels, entries = result
            if not hasattr(self.fm, "fig") or not self.fm.fig or not self.fm.fig.axes:
                continue
            bbox_to_anchor = self._get_legend_position(legend_index)
            title = self.generate_channel_title(channel, entries) if channel else None
            self.fm.fig.legend(
                handles,
                labels,
                title=title,
                loc=self.config.position,
                bbox_to_anchor=bbox_to_anchor,
                ncol=self.calculate_optimal_ncol(entries),
                frameon=self.fm.styler.get_style("legend_frameon", default=True),
            )
