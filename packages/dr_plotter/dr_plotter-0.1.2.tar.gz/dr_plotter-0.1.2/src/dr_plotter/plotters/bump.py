from __future__ import annotations

from typing import Any, ClassVar

import matplotlib.patheffects as path_effects
import pandas as pd

from dr_plotter.configs import GroupingConfig
from dr_plotter.theme import BUMP_PLOT_THEME, Theme
from dr_plotter.types import ComponentSchema, Phase, VisualChannel

from .base import BasePlotter


class BumpPlotter(BasePlotter):
    plotter_name: str = "bump"
    plotter_params: ClassVar[list[str]] = [
        "time_col",
        "category_col",
        "value_col",
        "rank_spacing",
    ]
    enabled_channels: ClassVar[set[VisualChannel]] = {"hue", "style"}
    default_theme: ClassVar[Theme] = BUMP_PLOT_THEME
    supports_grouped: bool = False

    component_schema: ClassVar[dict[Phase, ComponentSchema]] = {
        "plot": {
            "main": {
                "color",
                "linestyle",
                "linewidth",
                "marker",
                "markersize",
                "alpha",
                "label",
            }
        },
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
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

    def _initialize_subplot_specific_params(self) -> None:
        self.time_col = self.kwargs.get("time_col")
        self.value_col = self.kwargs.get("value_col")
        self.category_col = self.kwargs.get("category_col")
        self.rank_spacing = self.kwargs.get("rank_spacing", 1)

    def _plot_specific_data_prep(self) -> None:
        self.plot_data["rank"] = self.plot_data.groupby(self.time_col)[
            self.value_col
        ].rank(method="first", ascending=False)
        self.value_col = "rank"

        categories = self.plot_data[self.category_col].unique()
        self.trajectory_data = []

        for _i, category in enumerate(categories):
            cat_data = self.plot_data[self.plot_data[self.category_col] == category]
            cat_data = cat_data.sort_values(by=self.time_col).copy()

            color_styles = self.style_engine.cycle_cfg.get_styled_value_for_channel(
                "hue", category
            )
            style = {
                "color": color_styles.get("color", "#1f77b4"),
                "linestyle": "-",
            }

            cat_data["_bump_color"] = style["color"]
            cat_data["_bump_linestyle"] = style.get("linestyle", "-")
            cat_data["_bump_label"] = str(category)

            self.trajectory_data.append(cat_data)

    def _resolve_computed_parameters(
        self, _phase: str, _context: dict
    ) -> dict[str, Any]:
        return {}

    # TODO: Check if data parameter should be used instead of self.plot_data
    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:  # noqa: ARG002
        # Configure axis once before drawing trajectories
        self._configure_bump_axes(ax)

        for traj_data in self.trajectory_data:
            if not traj_data.empty:
                # First get the base configuration from the new system
                config = self._resolve_phase_config("main", **kwargs)

                # Then override with trajectory-specific color and style
                config.update(
                    {
                        "color": traj_data["_bump_color"].iloc[0],
                        "linestyle": traj_data["_bump_linestyle"].iloc[0],
                    }
                )

                lines = ax.plot(
                    traj_data[self.time_col],
                    traj_data[self.value_col],
                    **config,
                )

                last_point = traj_data.iloc[-1]
                category_name = traj_data["_bump_label"].iloc[0]
                text = ax.text(
                    last_point[self.time_col],
                    last_point[self.value_col],
                    f" {category_name}",
                    va="center",
                    color=self.styler.get_style("text_color", "black"),
                    fontweight=self.styler.get_style("fontweight", "bold"),
                )
                text.set_path_effects(
                    [
                        path_effects.Stroke(linewidth=2, foreground="white"),
                        path_effects.Normal(),
                    ]
                )

                self._register_legend_entry_if_valid(lines[0], category_name)

    def _configure_bump_axes(self, ax: Any) -> None:
        ax.invert_yaxis()
        max_rank = int(self.plot_data["rank"].max())
        ax.set_yticks(range(1, max_rank + 1))
        ax.margins(x=0.15)
        ax.set_ylabel(self.styler.get_style("ylabel", "Rank"))
