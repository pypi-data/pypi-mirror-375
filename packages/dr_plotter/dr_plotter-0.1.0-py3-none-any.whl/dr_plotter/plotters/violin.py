from __future__ import annotations

from typing import Any, ClassVar

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from dr_plotter import consts
from dr_plotter.artist_utils import (
    extract_single_alpha_from_polycollection_list,
    extract_single_color_from_polycollection_list,
    extract_single_edgecolor_from_polycollection_list,
)
from dr_plotter.configs import GroupingConfig
from dr_plotter.theme import VIOLIN_THEME, Theme
from dr_plotter.types import (
    ComponentSchema,
    Phase,
    VisualChannel,
)

from .base import BasePlotter


class ViolinPlotter(BasePlotter):
    plotter_name: str = "violin"
    plotter_params: ClassVar[list[str]] = [
        "alpha",
        "color",
        "label",
        "hue_by",
        "marker_by",
        "style_by",
        "size_by",
    ]
    enabled_channels: ClassVar[set[VisualChannel]] = {"hue"}
    default_theme: ClassVar[Theme] = VIOLIN_THEME

    component_schema: ClassVar[dict[Phase, ComponentSchema]] = {
        "plot": {
            "main": {
                "showmeans",
                "showmedians",
                "showextrema",
                "widths",
                "points",
            }
        },
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
            "bodies": {"facecolor", "edgecolor", "alpha", "linewidth"},
            "stats": {"color", "linewidth", "linestyle"},
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
            "violin", "bodies", self._style_violin_bodies
        )
        self.styler.register_post_processor("violin", "stats", self._style_violin_stats)

    def _style_violin_bodies(self, bodies: Any, styles: dict[str, Any]) -> None:
        for pc in bodies:
            for attr, value in styles.items():
                if attr == "facecolor" and hasattr(pc, "set_facecolor"):
                    pc.set_facecolor(value)
                elif attr == "edgecolor" and hasattr(pc, "set_edgecolor"):
                    pc.set_edgecolor(value)
                elif attr == "alpha" and hasattr(pc, "set_alpha"):
                    pc.set_alpha(value)
                elif attr == "linewidth" and hasattr(pc, "set_linewidth"):
                    pc.set_linewidth(value)

    def _style_violin_stats(self, stats: Any, styles: dict[str, Any]) -> None:
        for attr, value in styles.items():
            if attr == "color" and hasattr(stats, "set_edgecolor"):
                stats.set_edgecolor(value)
            elif attr == "linewidth" and hasattr(stats, "set_linewidth"):
                stats.set_linewidth(value)
            elif attr == "linestyle" and hasattr(stats, "set_linestyle"):
                stats.set_linestyle(value)
            elif hasattr(stats, f"set_{attr}"):
                setter = getattr(stats, f"set_{attr}")
                setter(value)

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        if not self._has_groups:
            self._draw_simple(ax, data, **kwargs)

    def _apply_post_processing(
        self, parts: dict[str, Any], label: str | None = None
    ) -> None:
        artists = self._collect_artists_to_style(parts)
        self.styler.apply_post_processing("violin", artists)
        if self._should_create_legend():
            label = (
                label
                if label is not None
                else self.styler.get_style("missing_label_str")
            )
            proxy = self._create_proxy_artist_from_bodies(parts["bodies"])
            self._register_legend_entry_if_valid(proxy, label)

    def _collect_artists_to_style(self, parts: dict[str, Any]) -> dict[str, Any]:
        assert "bodies" in parts, "Bodies must be present"

        stats_parts = []

        # Handle all conditional parts based on configuration
        for sub_part, gate_key in [
            ("cbars", "showextrema"),
            ("cmeans", "showmeans"),
            ("cmedians", "showmedians"),
            ("cmins", "showextrema"),
            ("cmaxes", "showextrema"),
        ]:
            if self.styler.get_style(gate_key):
                stats_parts.append(parts[sub_part])
        return {
            "stats": stats_parts,
            "bodies": parts["bodies"],
        }

    def _create_proxy_artist_from_bodies(self, bodies: list[Any]) -> Patch | None:
        if not bodies:
            return None

        facecolor = extract_single_color_from_polycollection_list(bodies)
        edgecolor = extract_single_edgecolor_from_polycollection_list(bodies)
        alpha = extract_single_alpha_from_polycollection_list(bodies)

        return Patch(facecolor=facecolor, edgecolor=edgecolor, alpha=alpha)

    def _draw_simple(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        groups = []
        group_data = [data]
        if consts.X_COL_NAME in data.columns:
            groups = data[consts.X_COL_NAME].unique()
            group_data = [data[data[consts.X_COL_NAME] == group] for group in groups]
        datasets = [gd[consts.Y_COL_NAME].dropna() for gd in group_data]

        label = kwargs.pop("label", None)
        config = self._resolve_phase_config("main", **kwargs)
        parts = ax.violinplot(datasets, **config)

        if len(groups) > 0:
            ax.set_xticks(np.arange(1, len(groups) + 1))
            ax.set_xticklabels(groups)

        self._apply_post_processing(parts, label)

    def _draw_grouped(
        self,
        ax: Any,
        data: pd.DataFrame,
        group_position: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        label = kwargs.pop("label", None)
        has_x_labels = consts.X_COL_NAME in data.columns
        config = self._resolve_phase_config("main", **kwargs)
        if "widths" not in config and "width" in group_position:
            config["widths"] = group_position["width"]
        elif "widths" in config and "width" in group_position:
            print("WARNING: Calculated width overridden by kwargs or theme")

        if has_x_labels:
            x_categories = group_position.get("x_categories")
            if x_categories is None:
                x_categories = data[consts.X_COL_NAME].unique()

            dataset = []
            positions = []
            for i, cat in enumerate(x_categories):
                cat_data = data[data[consts.X_COL_NAME] == cat][
                    consts.Y_COL_NAME
                ].dropna()
                if not cat_data.empty:
                    dataset.append(cat_data)
                    positions.append(i + group_position["offset"])

            if dataset:
                parts = ax.violinplot(
                    dataset,
                    positions=positions,
                    **config,
                )
            else:
                parts = {}

            if group_position["index"] == 0:
                ax.set_xticks(np.arange(len(x_categories)))
                ax.set_xticklabels(x_categories)
        else:
            parts = ax.violinplot(
                [data[consts.Y_COL_NAME].dropna()],
                positions=[group_position["offset"]],
                **config,
            )

        self._apply_post_processing(parts, label)
