from __future__ import annotations

from typing import TYPE_CHECKING
import matplotlib.axes

if TYPE_CHECKING:
    from dr_plotter.style_applicator import StyleApplicator


def apply_title_styling(
    ax: matplotlib.axes.Axes, styler: StyleApplicator, title_text: str | None = None
) -> None:
    if not title_text:
        title_text = styler.get_style("title")
    if title_text:
        title_kwargs = {
            "fontsize": styler.get_style("title_fontsize"),
        }
        title_color = styler.get_style("title_color")
        if title_color is not None:
            title_kwargs["color"] = title_color
        ax.set_title(title_text, **title_kwargs)


def apply_xlabel_styling(
    ax: matplotlib.axes.Axes, styler: StyleApplicator, xlabel_text: str | None = None
) -> None:
    if not xlabel_text:
        xlabel_text = styler.get_style("xlabel")
    if xlabel_text:
        xlabel_kwargs = {
            "fontsize": styler.get_style("label_fontsize"),
        }
        label_color = styler.get_style("label_color")
        if label_color is not None:
            xlabel_kwargs["color"] = label_color
        ax.set_xlabel(xlabel_text, **xlabel_kwargs)


def apply_ylabel_styling(
    ax: matplotlib.axes.Axes, styler: StyleApplicator, ylabel_text: str | None = None
) -> None:
    if not ylabel_text:
        ylabel_text = styler.get_style("ylabel")
    if ylabel_text:
        ylabel_kwargs = {
            "fontsize": styler.get_style("label_fontsize"),
        }
        label_color = styler.get_style("label_color")
        if label_color is not None:
            ylabel_kwargs["color"] = label_color
        ax.set_ylabel(ylabel_text, **ylabel_kwargs)


def apply_grid_styling(ax: matplotlib.axes.Axes, styler: StyleApplicator) -> None:
    grid_visible = styler.get_style("grid", default=True)
    if grid_visible:
        grid_kwargs = {
            "visible": True,
            "alpha": styler.get_style("grid_alpha", default=0.3),
            "linestyle": styler.get_style("grid_linestyle", default="-"),
        }
        grid_color = styler.get_style("grid_color")
        if grid_color is not None:
            grid_kwargs["color"] = grid_color
        ax.grid(**grid_kwargs)
    else:
        ax.grid(visible=False)
