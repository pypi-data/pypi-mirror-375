from __future__ import annotations

from typing import Any, ClassVar

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from dr_plotter import consts
from dr_plotter.configs import GroupingConfig
from dr_plotter.theme import SCATTER_THEME, Theme
from dr_plotter.types import (
    ComponentSchema,
    Phase,
    VisualChannel,
)

from .base import BasePlotter


class ScatterPlotter(BasePlotter):
    plotter_name: str = "scatter"
    plotter_params: ClassVar[list[str]] = []
    enabled_channels: ClassVar[set[VisualChannel]] = {"hue", "size", "marker", "alpha"}
    default_theme: ClassVar[Theme] = SCATTER_THEME

    component_schema: ClassVar[dict[Phase, ComponentSchema]] = {
        "plot": {
            "main": {
                "s",
                "alpha",
                "color",
                "marker",
                "edgecolors",
                "linewidths",
                "c",
                "cmap",
                "vmin",
                "vmax",
            }
        },
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
            "collection": {
                "sizes",
                "facecolors",
                "edgecolors",
                "linewidths",
                "alpha",
            },
        },
    }

    def __init__(
        self,
        data: pd.DataFrame,
        grouping_cfg: GroupingConfig,
        theme: Theme | None = None,
        figure_manager: Any | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)
        self.styler.register_post_processor(
            "scatter", "collection", self._style_scatter_collection
        )

    def _style_scatter_collection(
        self, collection: Any, styles: dict[str, Any]
    ) -> None:
        for attr, value in styles.items():
            if attr == "sizes" and hasattr(collection, "set_sizes"):
                collection.set_sizes([value])
            elif attr == "facecolors" and hasattr(collection, "set_facecolors"):
                collection.set_facecolors(value)
            elif attr == "edgecolors" and hasattr(collection, "set_edgecolors"):
                collection.set_edgecolors(value)
            elif attr == "linewidths" and hasattr(collection, "set_linewidths"):
                collection.set_linewidths(value)
            elif attr == "alpha" and hasattr(collection, "set_alpha"):
                collection.set_alpha(value)
            elif hasattr(collection, f"set_{attr}"):
                setter = getattr(collection, f"set_{attr}")
                setter(value)

    def _resolve_computed_parameters(
        self, phase: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        if phase != "main":
            return {}

        computed = {}
        if "size" in self.grouping_params.active_channels:
            size_col = self.grouping_params.size
            assert (
                size_col is not None
                and size_col in context.get("data", pd.DataFrame()).columns
            ), "Size column is required when grouped by size"
            data = context["data"]
            base_size = context.get("s", 50)
            sizes = []
            for value in data[size_col]:
                style = self.style_engine.get_continuous_style("size", size_col, value)
                size_mult = style.get("size_mult", 1.0)
                assert isinstance(base_size, (int, float)), (
                    f"Base size must be numeric, got {type(base_size)}: {base_size}"
                )
                sizes.append(base_size * size_mult)
            computed["s"] = sizes

        return computed

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        label = kwargs.pop("label", None)
        config = self._resolve_phase_config("main", data=data, **kwargs)

        collection = ax.scatter(
            data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **config
        )

        artists = {"collection": collection}
        self.styler.apply_post_processing("scatter", artists)

        self._apply_post_processing(collection, label)

    def _apply_post_processing(self, collection: Any, label: str | None = None) -> None:
        if not self._should_create_legend():
            return

        if self.figure_manager and label and collection:
            for channel in self.grouping_params.active_channels_ordered:
                proxy = self._create_channel_specific_proxy(collection)
                if proxy:
                    entry = self.styler.create_legend_entry(
                        proxy, label, self.current_axis, explicit_channel=channel
                    )
                    if entry:
                        self.figure_manager.register_legend_entry(entry)

    def _create_channel_specific_proxy(self, collection: Any) -> Any | None:
        facecolors = collection.get_facecolors()
        edgecolors = collection.get_edgecolors()
        sizes = collection.get_sizes()
        assert len(facecolors) > 0
        assert len(edgecolors) > 0

        face_color = facecolors[0]
        edge_color = edgecolors[0]
        marker_size = self.styler.get_style("marker_size", 8)
        if len(sizes) > 0:
            marker_size = np.sqrt(sizes[0] / np.pi) * 2
        marker_style = "o"
        if self.styler.group_values:
            styles = self.style_engine.get_styles_for_group(
                self.styler.group_values, self.grouping_params
            )
            marker_style = styles.get("marker", "o")

        proxy = Line2D(
            [0],
            [0],
            marker=marker_style,
            color="none",
            markerfacecolor=face_color,
            markeredgecolor=edge_color,
            markersize=marker_size,
            linestyle="",
        )
        return proxy
