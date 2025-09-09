from __future__ import annotations
import itertools
from typing import Any, TYPE_CHECKING

from dr_plotter import consts

if TYPE_CHECKING:
    from dr_plotter.configs import LegendConfig

ALPHA_MIN_DEFAULT = 0.3
ALPHA_MAX_DEFAULT = 1.0
DEFAULT_TEXT_FONTSIZE = 10


class Style:
    style_type = "general"

    def __init__(
        self,
        name: str | None = None,
        styles_to_merge: list[Style] | None = None,
        **styles: Any,
    ) -> None:
        if styles_to_merge is None:
            styles_to_merge = []
        self.name = name
        self.styles: dict[str, Any] = {**styles}
        self.merged_names: list[str] = []
        for style in styles_to_merge:
            self.merge_style(style)
            if style.name is not None:
                self.merged_names.append(style.name)

    def add(self, key: str, value: Any) -> None:
        self.styles[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.styles.get(key, default)

    def merge_style(self, other: Style) -> None:
        self.styles.update(other.styles)


class PlotStyles(Style):
    style_type = "plot"

    @classmethod
    def from_input(cls, value: dict | PlotStyles | None) -> PlotStyles:
        if value is None:
            return cls()
        elif isinstance(value, cls):
            return value
        elif isinstance(value, dict):
            return cls(**value)
        else:
            raise TypeError(f"Cannot create {cls.__name__} from {type(value).__name__}")


class PostStyles(Style):
    style_type = "post"

    @classmethod
    def from_input(cls, value: dict | PostStyles | None) -> PostStyles:
        if value is None:
            return cls()
        elif isinstance(value, cls):
            return value
        elif isinstance(value, dict):
            return cls(**value)
        else:
            raise TypeError(f"Cannot create {cls.__name__} from {type(value).__name__}")


class AxesStyles(Style):
    style_type = "axes"

    @classmethod
    def from_input(cls, value: dict | AxesStyles | None) -> AxesStyles:
        if value is None:
            return cls()
        elif isinstance(value, cls):
            return value
        elif isinstance(value, dict):
            return cls(**value)
        else:
            raise TypeError(f"Cannot create {cls.__name__} from {type(value).__name__}")


class FigureStyles(Style):
    style_type = "figure"

    @classmethod
    def from_input(cls, value: dict | FigureStyles | None) -> FigureStyles:
        if value is None:
            return cls()
        elif isinstance(value, cls):
            return value
        elif isinstance(value, dict):
            return cls(**value)
        else:
            raise TypeError(f"Cannot create {cls.__name__} from {type(value).__name__}")


class Theme:
    def __init__(
        self,
        name: str,
        parent: Theme | None = None,
        plot_styles: PlotStyles | dict | None = None,
        post_styles: PostStyles | dict | None = None,
        axes_styles: AxesStyles | dict | None = None,
        figure_styles: FigureStyles | dict | None = None,
        legend_config: LegendConfig | None = None,
        **styles: Any,
    ) -> None:
        self.name = name
        self.parent = parent
        if legend_config is not None:
            self.legend_config = legend_config
        elif parent and parent.legend_config:
            self.legend_config = parent.legend_config
        else:
            from dr_plotter.configs.legend_config import LegendConfig

            self.legend_config = LegendConfig()
        self.all_styles: dict[str, Style] = {}
        self.all_styles["plot"] = PlotStyles.from_input(plot_styles)
        self.all_styles["post"] = PostStyles.from_input(post_styles)
        self.all_styles["axes"] = AxesStyles.from_input(axes_styles)
        self.all_styles["figure"] = FigureStyles.from_input(figure_styles)

        if styles is not None:
            self.all_styles["general"] = (
                Style(**styles) if isinstance(styles, dict) else styles
            )
        else:
            self.all_styles["general"] = Style()

    @property
    def general_styles(self) -> dict[str, Any]:
        return self.get_all_styles(Style)

    @property
    def plot_styles(self) -> dict[str, Any]:
        return self.get_all_styles(PlotStyles)

    @property
    def post_styles(self) -> dict[str, Any]:
        return self.get_all_styles(PostStyles)

    @property
    def axes_styles(self) -> dict[str, Any]:
        return self.get_all_styles(AxesStyles)

    @property
    def figure_styles(self) -> dict[str, Any]:
        return self.get_all_styles(FigureStyles)

    def get_all_styles(self, cls: type) -> dict[str, Any]:
        styles: dict[str, Any] = {}
        if self.parent is not None:
            styles.update(self.parent.get_all_styles(cls))
        styles.update(self.all_styles[cls.style_type].styles)
        return styles

    def get(self, key: str, default: Any = None, source: str | None = None) -> Any:
        for source_type, source_styles in self.all_styles.items():
            if (source is None or source_type == source) and (
                key in source_styles.styles
            ):
                return source_styles.get(key)
        if self.parent:
            return self.parent.get(key, default=default, source=source)
        return default

    def add(self, key: str, value: Any, source: str | None = None) -> None:
        source = source if source is not None else Style.style_type
        self.all_styles[source].add(key, value)


BASE_COLORS = [
    "#4C72B0",
    "#55A868",
    "#C44E52",
    "#8172B2",
    "#CCB974",
    "#64B5CD",
    "#DA816D",
    "#8E8E8E",
]

BASE_THEME = Theme(
    name="base",
    axes_styles=AxesStyles(
        grid=True,
        grid_alpha=0.3,
        label_fontsize=12,
        legend_fontsize=10,
        cmap="viridis",
        colorbar_size="5%",
        colorbar_pad=0.1,
    ),
    figure_styles=FigureStyles(
        title_fontsize=14,
        suptitle_fontsize=16,
        suptitle_y=0.99,
    ),
    error_color="#FF0000",
    error_edge_color="#FF0000",
    default_color=BASE_COLORS[0],
    text_color="#000000",
    text_fontsize=DEFAULT_TEXT_FONTSIZE,
    text_ha="center",
    text_va="center",
    alpha_min=ALPHA_MIN_DEFAULT,
    alpha_max=ALPHA_MAX_DEFAULT,
    missing_label_str="(empty label)",
    **{
        consts.get_cycle_key("hue"): itertools.cycle(BASE_COLORS),
        consts.get_cycle_key("style"): itertools.cycle(["-", "--", ":", "-."]),
        consts.get_cycle_key("marker"): itertools.cycle(
            ["o", "s", "^", "D", "v", "<", ">", "p"]
        ),
        consts.get_cycle_key("size"): itertools.cycle([1.0, 1.5, 2.0, 2.5]),
        consts.get_cycle_key("alpha"): itertools.cycle([1.0, 0.7, 0.5, 0.3]),
    },
)

DARK_X_AXIS_STYLE = AxesStyles(
    name="dark_x_axis",
    **{
        "axes.axisbelow": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.spines.bottom": True,
    },
)

LINE_THEME = Theme(
    name="line",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        marker=None,
        linewidth=2.0,
    ),
)

SCATTER_THEME = Theme(
    name="scatter",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        alpha=1.0,
        s=50,
    ),
)

BAR_THEME = Theme(
    name="bar",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        alpha=0.8,
    ),
    axes_styles=AxesStyles(
        styles_to_merge=[DARK_X_AXIS_STYLE],
    ),
)

HISTOGRAM_THEME = Theme(
    name="histogram",
    parent=BAR_THEME,
    plot_styles=PlotStyles(
        edgecolor="white",
    ),
    axes_styles=AxesStyles(
        ylabel="Count",
    ),
)

VIOLIN_THEME = Theme(
    name="violin",
    parent=BASE_THEME,
    plot_styles=PlotStyles(
        showmeans=True,
    ),
    axes_styles=AxesStyles(
        styles_to_merge=[DARK_X_AXIS_STYLE],
    ),
    alpha=0.7,
    linewidth=1.5,
    edgecolor="black",
)

HEATMAP_THEME = Theme(
    name="heatmap",
    parent=BASE_THEME,
    text_color="#FFFFFF",
    text_fontsize=8,
    axes_styles=AxesStyles(
        grid=False,
        xlabel_pos="top",
    ),
)

BUMP_PLOT_THEME = Theme(
    name="bump",
    parent=LINE_THEME,
    plot_styles=PlotStyles(
        linewidth=3.0,
        marker="o",
    ),
    axes_styles=AxesStyles(
        legend=False,
        ylabel="Rank",
    ),
    **{
        consts.get_cycle_key("hue"): itertools.cycle(
            [
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",
                "#9467bd",
                "#8c564b",
                "#e377c2",
                "#7f7f7f",
                "#bcbd22",
                "#17becf",
            ]
        ),
    },
)

CONTOUR_THEME = Theme(
    name="contour",
    parent=BASE_THEME,
    levels=14,
    scatter_alpha=0.5,
    scatter_size=10,
)

GROUPED_BAR_THEME = Theme(
    name="grouped_bar",
    parent=BAR_THEME,
    plot_styles=PlotStyles(
        rotation=0,
    ),
)
