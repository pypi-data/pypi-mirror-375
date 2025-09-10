from typing import Any

PUBLICATION_COLORS = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D"]
BUMP_OPTIMIZED_PALETTE = [
    "#FF6B6B",
    "#4ECDC4",
    "#45B7D1",
    "#96CEB4",
    "#FFEAA7",
    "#DDA0DD",
]

TEMPORAL_OPTIMIZED_PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
]
DISTRIBUTION_PALETTE = [
    "#3182bd",
    "#fd8d3c",
    "#74c476",
    "#f03b20",
    "#9e9ac8",
    "#bcbddc",
]
HIGH_DIMENSIONAL_PALETTE = [
    "#e41a1c",
    "#377eb8",
    "#4daf4a",
    "#984ea3",
    "#ff7f00",
    "#ffff33",
    "#a65628",
    "#f781bf",
]
COLORBLIND_SAFE_PALETTE = [
    "#0173b2",
    "#de8f05",
    "#029e73",
    "#cc78bc",
    "#ca9161",
    "#fbafe4",
    "#949494",
    "#ece133",
]
HIGH_CONTRAST_PALETTE = [
    "#000000",
    "#e69f00",
    "#56b4e9",
    "#009e73",
    "#f0e442",
    "#0072b2",
    "#d55e00",
    "#cc79a7",
]
HIGH_VISIBILITY_PALETTE = [
    "#2E86AB",
    "#A23B72",
    "#F18F01",
    "#C73E1D",
    "#5D2E8B",
    "#228B22",
]
NOTEBOOK_PALETTE = ["#4472C4", "#E70200", "#70AD47", "#7030A0", "#FF6600", "#264478"]

PLOT_CONFIGS: dict[str, dict[str, Any]] = {
    "default": {
        "layout": (1, 1),
        "style": {"theme": "base"},
        "legend": {"style": "subplot"},
    },
    "dashboard": {
        "layout": {"rows": 2, "cols": 2, "figsize": (16, 12), "tight_layout_pad": 0.3},
        "legend": {"style": "grouped"},
    },
    "publication": {
        "layout": {"figsize": (12, 8), "tight_layout_pad": 0.8},
        "style": {
            "colors": PUBLICATION_COLORS,
            "fonts": {"size": 12},
            "figure_styles": {"dpi": 300},
        },
        "legend": {"style": "figure"},
    },
    "bump_plot": {
        "style": {
            "colors": BUMP_OPTIMIZED_PALETTE,
            "theme": "line",
            "plot_styles": {"linewidth": 3, "marker": "o"},
        },
        "legend": {"style": "grouped"},
    },
    "faceted_analysis": {
        "layout": {"rows": 3, "cols": 2, "figsize": (14, 16)},
        "legend": {"style": "figure"},
    },
    "time_series": {
        "style": {
            "colors": TEMPORAL_OPTIMIZED_PALETTE,
            "plot_styles": {"linewidth": 2, "alpha": 0.8, "marker": None},
            "theme": "line",
        },
        "legend": {"style": "figure"},
        "layout": {"figsize": (14.0, 6.0)},
    },
    "distribution_analysis": {
        "style": {
            "colors": DISTRIBUTION_PALETTE,
            "plot_styles": {"alpha": 0.7, "edgecolor": "black", "linewidth": 0.5},
            "theme": "base",
        },
        "legend": {"style": "subplot"},
        "layout": {"figsize": (12.0, 8.0)},
    },
    "scatter_matrix": {
        "style": {
            "colors": HIGH_DIMENSIONAL_PALETTE,
            "plot_styles": {"s": 30, "alpha": 0.6, "edgecolors": "none"},
            "theme": "scatter",
        },
        "legend": {"style": "grouped"},
        "layout": {"figsize": (16.0, 16.0), "tight_layout_pad": 0.4},
    },
    "presentation": {
        "style": {
            "colors": HIGH_VISIBILITY_PALETTE,
            "fonts": {"size": 16},
            "plot_styles": {"linewidth": 4, "markersize": 8},
            "figure_styles": {"dpi": 150},
        },
        "legend": {"style": "figure"},
        "layout": {"figsize": (16.0, 9.0)},
    },
    "notebook": {
        "style": {
            "colors": NOTEBOOK_PALETTE,
            "fonts": {"size": 10},
            "plot_styles": {"linewidth": 1.5, "markersize": 4},
        },
        "legend": {"style": "subplot"},
        "layout": {"figsize": (10.0, 6.0), "tight_layout_pad": 0.2},
    },
    "colorblind_safe": {
        "style": {
            "colors": COLORBLIND_SAFE_PALETTE,
            "plot_styles": {"linewidth": 2, "linestyle": "solid"},
        },
        "legend": {"style": "subplot"},
    },
    "high_contrast": {
        "style": {
            "colors": HIGH_CONTRAST_PALETTE,
            "plot_styles": {"linewidth": 3, "edgecolor": "black"},
        },
        "legend": {"style": "subplot"},
    },
    "minimal": {
        "style": {
            "colors": ["#333333", "#666666", "#999999", "#CCCCCC"],
            "plot_styles": {"linewidth": 1, "alpha": 0.8},
            "theme": "base",
        },
        "legend": {"style": "none"},
        "layout": {"figsize": (10.0, 6.0), "tight_layout_pad": 0.1},
    },
    "vibrant": {
        "style": {
            "colors": [
                "#FF6B35",
                "#004E89",
                "#009639",
                "#FFD23F",
                "#EE4266",
                "#7209B7",
            ],
            "plot_styles": {"linewidth": 2.5, "alpha": 0.9},
            "theme": "base",
        },
        "legend": {"style": "figure"},
    },
    "scientific": {
        "style": {
            "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
            "fonts": {"size": 11},
            "plot_styles": {"linewidth": 1.5, "alpha": 0.8},
            "figure_styles": {"dpi": 300},
        },
        "legend": {"style": "subplot"},
        "layout": {"figsize": (8.0, 6.0), "tight_layout_pad": 0.5},
    },
}
