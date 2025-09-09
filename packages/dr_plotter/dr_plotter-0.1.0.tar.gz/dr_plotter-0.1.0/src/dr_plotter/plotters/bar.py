from __future__ import annotations

from typing import Any, ClassVar

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from dr_plotter import consts
from dr_plotter.configs import GroupingConfig
from dr_plotter.theme import BAR_THEME, Theme
from dr_plotter.types import (
    ComponentSchema,
    Phase,
    VisualChannel,
)

from .base import BasePlotter


class BarPlotter(BasePlotter):
    plotter_name: str = "bar"
    plotter_params: ClassVar[list[str]] = []
    enabled_channels: ClassVar[set[VisualChannel]] = {"hue"}
    default_theme: ClassVar[Theme] = BAR_THEME

    component_schema: ClassVar[dict[Phase, ComponentSchema]] = {
        "plot": {
            "main": {
                "color",
                "alpha",
                "edgecolor",
                "linewidth",
                "width",
                "bottom",
                "align",
                "label",
            }
        },
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
            "patches": {"facecolor", "edgecolor", "alpha", "linewidth"},
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
        self.styler.register_post_processor("bar", "patches", self._style_bar_patches)

    def _style_bar_patches(self, patches: Any, styles: dict[str, Any]) -> None:
        for patch in patches:
            for attr, value in styles.items():
                if hasattr(patch, f"set_{attr}"):
                    setter = getattr(patch, f"set_{attr}")
                    setter(value)

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        if not self._has_groups:
            self._draw_simple(ax, data, **kwargs)

    def _draw_simple(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        label = kwargs.pop("label", None)
        config = self._resolve_phase_config("main", **kwargs)
        patches = ax.bar(data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **config)

        artists = {"patches": patches}
        self.styler.apply_post_processing("bar", artists)

        self._apply_post_processing(patches, label)

    def _apply_post_processing(self, patches: Any, label: str | None = None) -> None:
        if patches:
            first_patch = patches[0]
            proxy = Patch(
                facecolor=first_patch.get_facecolor(),
                edgecolor=first_patch.get_edgecolor(),
                alpha=first_patch.get_alpha(),
            )
            self._register_legend_entry_if_valid(proxy, label)

    def _draw_grouped(
        self,
        ax: Any,
        data: pd.DataFrame,
        group_position: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        label = kwargs.pop("label", None)

        x_categories = group_position.get("x_categories")
        if x_categories is None:
            x_categories = data[consts.X_COL_NAME].unique()

        x_positions = []
        y_values = []
        for i, cat in enumerate(x_categories):
            cat_data = data[data[consts.X_COL_NAME] == cat]
            if not cat_data.empty:
                x_positions.append(i + group_position["offset"])
                y_values.append(cat_data[consts.Y_COL_NAME].to_numpy()[0])

        patches = None
        if x_positions:
            config = self._resolve_phase_config(
                "main", width=group_position["width"], **kwargs
            )
            patches = ax.bar(x_positions, y_values, **config)

        if group_position["index"] == 0:
            ax.set_xticks(np.arange(len(x_categories)))
            ax.set_xticklabels(x_categories)

        self._apply_post_processing(patches, label)
