from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dr_plotter.configs.legend_config import LegendConfig, LegendStrategy
from dr_plotter.configs.positioning_config import PositioningConfig
from dr_plotter.positioning_calculator import (
    FigureDimensions,
    LegendMetadata,
    PositioningCalculator,
)


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
        self.strategy = strategy

    def add_entry(self, entry: LegendEntry) -> None:
        if self._should_use_channel_based_deduplication():
            key = (entry.visual_channel, entry.channel_value)
        else:
            key = (entry.label, id(entry.axis))

        if key not in self._seen_keys:
            self._entries.append(entry)
            self._seen_keys.add(key)

    def _should_use_channel_based_deduplication(self) -> bool:
        if self.strategy is None:
            return False
        shared_strategies = {
            LegendStrategy.GROUPED_BY_CHANNEL,
            LegendStrategy.FIGURE_BELOW,
        }
        return self.strategy in shared_strategies

    def get_unique_entries(self) -> list[LegendEntry]:
        return self._entries.copy()

    def get_by_channel(self, channel: str) -> list[LegendEntry]:
        return [e for e in self._entries if e.visual_channel == channel]

    def clear(self) -> None:
        self._entries.clear()
        self._seen_keys.clear()


def resolve_legend_config(legend_input: str | LegendConfig) -> LegendConfig:
    if isinstance(legend_input, str):
        positioning_config = PositioningConfig()
        grouped_config = PositioningConfig(default_margin_bottom=0.2)

        string_mappings = {
            "grouped": LegendConfig(
                strategy="grouped",
                layout_bottom_margin=0.2,
                positioning_config=grouped_config,
            ),
            "subplot": LegendConfig(
                strategy="subplot", positioning_config=positioning_config
            ),
            "figure": LegendConfig(
                strategy="figure", positioning_config=positioning_config
            ),
            "none": LegendConfig(
                strategy="none", positioning_config=positioning_config
            ),
        }
        assert legend_input in string_mappings, (
            f"Invalid legend string '{legend_input}'. Valid options: "
            f"{list(string_mappings.keys())}"
        )
        return string_mappings[legend_input]

    if legend_input.positioning_config is None:
        legend_input.positioning_config = PositioningConfig()

    return legend_input


class LegendManager:
    def __init__(self, figure_manager: Any, config: LegendConfig | None = None) -> None:
        self.fm = figure_manager
        self.config = config or LegendConfig()
        if self.config.positioning_config is None:
            self.config.positioning_config = PositioningConfig()
        self.positioning_calculator = PositioningCalculator(
            self.config.positioning_config
        )
        self.registry = LegendRegistry(self.config.strategy)

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

    def _get_figure_dimensions(self) -> FigureDimensions:
        figure_width = getattr(self.fm.fig, "get_figwidth", lambda: 10)()
        figure_height = getattr(self.fm.fig, "get_figheight", lambda: 8)()

        has_title = self.fm.fig._suptitle is not None  # noqa: SLF001
        has_subplot_titles = (
            self.fm._has_subplot_titles()  # noqa: SLF001
            if hasattr(self.fm, "_has_subplot_titles")
            else False
        )

        return FigureDimensions(
            width=figure_width,
            height=figure_height,
            rows=getattr(self.fm, "rows", 1),
            cols=getattr(self.fm, "cols", 1),
            has_title=has_title,
            has_subplot_titles=has_subplot_titles,
        )

    def calculate_optimal_positioning(
        self, num_legends: int, legend_index: int, figure_width: float | None = None
    ) -> tuple[float, float]:
        figure_dimensions = self._get_figure_dimensions()
        if figure_width:
            figure_dimensions.width = figure_width

        legend_metadata = LegendMetadata(
            num_legends=num_legends,
            num_handles_per_legend=1,
            strategy=self.config.strategy.value
            if hasattr(self.config.strategy, "value")
            else str(self.config.strategy),
        )

        result = self.positioning_calculator.calculate_positions(
            figure_dimensions, legend_metadata
        )

        default_pos = (
            self.config.positioning_config.legend_alignment_center,
            self.config.positioning_config.legend_y_offset_factor,
        )
        return result.legend_positions.get(legend_index, default_pos)

    def finalize(self) -> None:
        if self.config.strategy == LegendStrategy.NONE:
            return

        if self.config.strategy == LegendStrategy.FIGURE_BELOW:
            self._create_figure_legend()
        elif self.config.strategy == LegendStrategy.GROUPED_BY_CHANNEL:
            self._create_grouped_legends()
        elif self.config.strategy == LegendStrategy.PER_AXES:
            self._create_per_axes_legends()

    def _process_entries_by_channel_type(
        self, entries: list[LegendEntry]
    ) -> list[LegendEntry]:
        return entries

    def _create_figure_legend(self) -> None:
        entries = self.registry.get_unique_entries()

        if not entries:
            return

        entries = self._process_entries_by_channel_type(entries)

        handles = []
        labels = []

        for entry in entries:
            handles.append(entry.artist)
            labels.append(entry.label)

        if hasattr(self.fm, "fig") and self.fm.fig:
            ncol = self._calculate_ncol(len(handles))

            figure_dimensions = self._get_figure_dimensions()
            legend_metadata = LegendMetadata(
                num_legends=1,
                num_handles_per_legend=len(handles),
                strategy=self.config.strategy.value
                if hasattr(self.config.strategy, "value")
                else str(self.config.strategy),
            )

            result = self.positioning_calculator.calculate_positions(
                figure_dimensions, legend_metadata
            )

            default_pos = (
                self.config.positioning_config.legend_alignment_center,
                self.config.positioning_config.legend_y_offset_factor,
            )
            bbox_to_anchor = result.legend_positions.get(0, default_pos)

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
                frameon=False,
            )

            if self.config.remove_axes_legends:
                for ax in self.fm.fig.axes:
                    legend = ax.get_legend()
                    if legend:
                        legend.remove()

    def _create_per_axes_legends(self) -> None:
        entries = self.registry.get_unique_entries()
        if not entries:
            return

        entries = self._process_entries_by_channel_type(entries)

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

        if self.config.strategy == LegendStrategy.GROUPED_BY_CHANNEL:
            num_legends = len(channel_list)
            legends_to_create = [(i, channel) for i, channel in enumerate(channel_list)]
        elif self.config.strategy == LegendStrategy.FIGURE_BELOW:
            num_legends = 1
            legends_to_create = [(0, None)]
        else:
            return

        for legend_index, channel in legends_to_create:
            if channel is not None:
                entries = self.registry.get_by_channel(channel)
            else:
                entries = self.registry.get_unique_entries()

            if not entries:
                continue

            entries = self._process_entries_by_channel_type(entries)

            handles = []
            labels = []

            for entry in entries:
                handles.append(entry.artist)
                labels.append(entry.label)

            if hasattr(self.fm, "fig") and self.fm.fig and self.fm.fig.axes:
                bbox_to_anchor = self.calculate_optimal_positioning(
                    num_legends, legend_index
                )

                title = None
                if channel:
                    title = self.generate_channel_title(channel, entries)

                self.fm.fig.legend(
                    handles,
                    labels,
                    title=title,
                    loc="upper center",
                    bbox_to_anchor=bbox_to_anchor,
                    ncol=self.calculate_optimal_ncol(entries),
                    frameon=True,
                )
