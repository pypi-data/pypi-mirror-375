from typing import Any

import numpy as np
import pandas as pd
from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import (
    inspect_plot_properties,
    verify_figure_legends,
)


def create_multi_channel_data() -> pd.DataFrame:
    base_data = ExampleData.get_cross_groupby_legends_data()

    np.random.seed(800)
    model_sizes = ["small_model", "medium_model", "large_model", "xl_model"]
    dataset_types = ["train_set", "val_set", "test_set"]

    records = []
    for i, row in base_data.iterrows():
        if i % 10 == 0:
            records.append(
                {
                    "performance": row["performance"],
                    "accuracy": row["accuracy"],
                    "runtime": row["runtime"],
                    "model_size": np.random.choice(model_sizes),
                    "dataset_type": np.random.choice(dataset_types),
                    "experiment": row["experiment"],
                    "condition": row["condition"],
                    "algorithm": row["algorithm"],
                }
            )

    return pd.DataFrame(records)


def section_1_subplot_string_interface(args: Any) -> Any:
    multi_channel_data = create_multi_channel_data()

    with FigureManager(
        PlotConfig(
            layout={"rows": 2, "cols": 2, "figsize": (16, 12)},
            legend={"strategy": "subplot"},
        )
    ) as fm:
        fm.fig.suptitle(
            'Section 1A: String Interface - legend="subplot"', fontsize=16, y=0.95
        )

        fm.plot(
            "scatter",
            0,
            0,
            multi_channel_data,
            x="performance",
            y="accuracy",
            hue_by="experiment",
            s=60,
            alpha=0.8,
            title="Subplot Legend - Experiment",
        )

        fm.plot(
            "scatter",
            0,
            1,
            multi_channel_data,
            x="performance",
            y="runtime",
            hue_by="condition",
            s=60,
            alpha=0.8,
            title="Subplot Legend - Condition",
        )

        fm.plot(
            "line",
            1,
            0,
            multi_channel_data.groupby(["experiment", "performance"])
            .agg({"accuracy": "mean"})
            .reset_index(),
            x="performance",
            y="accuracy",
            hue_by="experiment",
            linewidth=2,
            title="Line Plot with Subplot Legend",
        )

        fm.plot(
            "scatter",
            1,
            1,
            multi_channel_data,
            x="runtime",
            y="accuracy",
            hue_by="algorithm",
            s=60,
            alpha=0.8,
            title="Algorithm Grouping",
        )

    show_or_save_plot(fm.fig, args, "12_legend_showcase_section1_subplot")
    return fm.fig


@inspect_plot_properties()
@verify_figure_legends(
    expected_legend_count=1, legend_strategy="figure_below", expected_total_entries=3
)
def section_1_figure_string_interface(args: Any) -> Any:
    multi_channel_data = create_multi_channel_data()

    with FigureManager(
        PlotConfig(
            layout={"rows": 2, "cols": 2, "figsize": (16, 12)},
            legend={"strategy": "figure"},
        )
    ) as fm:
        fm.fig.suptitle(
            'Section 1B: String Interface - legend="figure"', fontsize=16, y=0.95
        )

        fm.plot(
            "scatter",
            0,
            0,
            multi_channel_data,
            x="performance",
            y="accuracy",
            hue_by="experiment",
            s=60,
            alpha=0.8,
            title="Contributing to Figure Legend",
        )

        fm.plot(
            "scatter",
            0,
            1,
            multi_channel_data,
            x="performance",
            y="runtime",
            hue_by="experiment",
            s=60,
            alpha=0.8,
            title="Same Channel - Shared Legend",
        )

        fm.plot(
            "line",
            1,
            0,
            multi_channel_data.groupby(["experiment", "performance"])
            .agg({"accuracy": "mean"})
            .reset_index(),
            x="performance",
            y="accuracy",
            hue_by="experiment",
            linewidth=2,
            title="Different Plot Type, Same Legend",
        )

        fm.plot(
            "scatter",
            1,
            1,
            multi_channel_data,
            x="runtime",
            y="accuracy",
            hue_by="experiment",
            s=60,
            alpha=0.8,
            title="Consistent Experiment Legend",
        )

    show_or_save_plot(fm.fig, args, "12_legend_showcase_section1_figure")
    return fm.fig


def section_2_grouped_string_interface(args: Any) -> Any:
    multi_channel_data = create_multi_channel_data()

    with FigureManager(
        PlotConfig(
            layout={"rows": 2, "cols": 2, "figsize": (16, 12)},
            legend={"strategy": "grouped"},
        )
    ) as fm:
        fm.fig.suptitle(
            'Section 2A: String Interface - legend="grouped" (Multi-Channel)',
            fontsize=16,
            y=0.93,
        )

        fm.plot(
            "scatter",
            0,
            0,
            multi_channel_data,
            x="performance",
            y="accuracy",
            hue_by="experiment",
            marker_by="condition",
            s=60,
            alpha=0.8,
            title="Multi-Channel: Experiment + Condition",
        )

        fm.plot(
            "scatter",
            0,
            1,
            multi_channel_data,
            x="performance",
            y="runtime",
            hue_by="model_size",
            marker_by="dataset_type",
            s=60,
            alpha=0.8,
            title="Context-Aware Titles from Column Names",
        )

        fm.plot(
            "scatter",
            1,
            0,
            multi_channel_data,
            x="runtime",
            y="accuracy",
            hue_by="algorithm",
            s=80,
            alpha=0.7,
            title="Single Channel for Comparison",
        )

        fm.plot(
            "scatter",
            1,
            1,
            multi_channel_data,
            x="performance",
            y="runtime",
            hue_by="experiment",
            marker_by="algorithm",
            s=60,
            alpha=0.8,
            title="Adaptive Layout & Responsive Positioning",
        )

    show_or_save_plot(fm.fig, args, "12_legend_showcase_section2_grouped")
    return fm.fig


def section_2_none_string_interface(args: Any) -> Any:
    multi_channel_data = create_multi_channel_data()

    with FigureManager(
        PlotConfig(
            layout={"rows": 2, "cols": 2, "figsize": (16, 12)},
            legend={"strategy": "none"},
        )
    ) as fm:
        fm.fig.suptitle(
            'Section 2B: String Interface - legend="none"', fontsize=16, y=0.95
        )

        fm.plot(
            "scatter",
            0,
            0,
            multi_channel_data,
            x="performance",
            y="accuracy",
            hue_by="experiment",
            s=60,
            alpha=0.8,
            title="No Legend - Visual Encoding Only",
        )

        fm.plot(
            "scatter",
            0,
            1,
            multi_channel_data,
            x="performance",
            y="runtime",
            hue_by="condition",
            s=60,
            alpha=0.8,
            title="Clean Layout Without Legends",
        )

        fm.plot(
            "line",
            1,
            0,
            multi_channel_data.groupby(["experiment", "performance"])
            .agg({"accuracy": "mean"})
            .reset_index(),
            x="performance",
            y="accuracy",
            hue_by="experiment",
            linewidth=2,
            title="Focus on Plot Content",
        )

        fm.plot(
            "scatter",
            1,
            1,
            multi_channel_data,
            x="runtime",
            y="accuracy",
            hue_by="algorithm",
            s=60,
            alpha=0.8,
            title="Maximum Plot Area Usage",
        )

    show_or_save_plot(fm.fig, args, "12_legend_showcase_section2_none")
    return fm.fig


@inspect_plot_properties()
@verify_figure_legends(
    expected_legend_count=1, legend_strategy="figure_below", expected_total_entries=3
)
def section_3_positioning_calculator_integration(args: Any) -> Any:
    positioning_data = create_multi_channel_data()

    with FigureManager(
        PlotConfig(
            layout={"rows": 1, "cols": 3, "figsize": (18, 6)},
            legend={
                "strategy": "figure",
                "ncol": None,
                "layout_bottom_margin": 0.15,
            },
        )
    ) as fm:
        fm.fig.suptitle(
            "Section 3: PositioningCalculator Integration - Figure-Width Responsive",
            fontsize=16,
            y=0.92,
        )

        fm.plot(
            "scatter",
            0,
            0,
            positioning_data,
            x="performance",
            y="accuracy",
            hue_by="experiment",
            s=60,
            alpha=0.8,
            title="Narrow: Systematic Positioning",
        )

        time_series_data = (
            positioning_data.groupby(["experiment", "performance"])
            .agg({"accuracy": "mean", "runtime": "mean"})
            .reset_index()
        )

        fm.plot(
            "line",
            0,
            1,
            time_series_data,
            x="performance",
            y="accuracy",
            hue_by="experiment",
            linewidth=2,
            alpha=0.8,
            title="Medium: Responsive Spacing",
        )

        fm.plot(
            "scatter",
            0,
            2,
            positioning_data,
            x="runtime",
            y="accuracy",
            hue_by="experiment",
            s=60,
            alpha=0.8,
            title="Wide: Adaptive Alignment",
        )

    show_or_save_plot(fm.fig, args, "12_legend_showcase_section3_positioning")
    return fm.fig


@inspect_plot_properties()
def section_4_layout_hints_demonstration(args: Any) -> Any:
    hint_data = create_multi_channel_data()

    # Section 4A: "below" hint
    with FigureManager(
        PlotConfig(
            layout={"rows": 1, "cols": 2, "figsize": (12, 6)},
            legend={"strategy": "figure", "layout_hint": "below"},
        )
    ) as fm_below:
        fm_below.fig.suptitle(
            'Section 4A: Layout Hints - layout_hint="below"', fontsize=16, y=0.95
        )

        fm_below.plot(
            "scatter",
            0,
            0,
            hint_data,
            x="performance",
            y="accuracy",
            hue_by="experiment",
            s=60,
            alpha=0.8,
            title="Bottom Positioning (y=0.05)",
        )

        fm_below.plot(
            "line",
            0,
            1,
            hint_data.groupby(["experiment", "performance"])
            .agg({"accuracy": "mean"})
            .reset_index(),
            x="performance",
            y="accuracy",
            hue_by="experiment",
            linewidth=2,
            alpha=0.8,
            title="Smart Bottom Center Layout",
        )

    show_or_save_plot(fm_below.fig, args, "12_legend_showcase_section4a_below")

    # Section 4B: "side" hint
    with FigureManager(
        PlotConfig(
            layout={"rows": 1, "cols": 2, "figsize": (12, 6)},
            legend={"strategy": "figure", "layout_hint": "side"},
        )
    ) as fm_side:
        fm_side.fig.suptitle(
            'Section 4B: Layout Hints - layout_hint="side"', fontsize=16, y=0.95
        )

        fm_side.plot(
            "scatter",
            0,
            0,
            hint_data,
            x="performance",
            y="runtime",
            hue_by="condition",
            s=60,
            alpha=0.8,
            title="Right-Side Positioning",
        )

        fm_side.plot(
            "scatter",
            0,
            1,
            hint_data,
            x="runtime",
            y="accuracy",
            hue_by="condition",
            s=60,
            alpha=0.8,
            title="Responsive to Figure Width",
        )

    show_or_save_plot(fm_side.fig, args, "12_legend_showcase_section4b_side")

    # Section 4C: "compact" vs "spacious" comparison
    with FigureManager(
        PlotConfig(
            layout={"rows": 1, "cols": 2, "figsize": (16, 6)},
            legend={"strategy": "figure", "layout_hint": "compact"},
        )
    ) as fm_compact:
        fm_compact.fig.suptitle(
            'Section 4C: Layout Hints - layout_hint="compact"', fontsize=16, y=0.95
        )

        fm_compact.plot(
            "scatter",
            0,
            0,
            hint_data,
            x="performance",
            y="accuracy",
            hue_by="algorithm",
            s=60,
            alpha=0.8,
            title="Compact Spacing (y_offset=-0.02)",
        )

        fm_compact.plot(
            "scatter",
            0,
            1,
            hint_data,
            x="runtime",
            y="performance",
            hue_by="algorithm",
            s=60,
            alpha=0.8,
            title="Minimized Legend Space",
        )

    show_or_save_plot(fm_compact.fig, args, "12_legend_showcase_section4c_compact")

    # Section 4D: "spacious" hint
    with FigureManager(
        PlotConfig(
            layout={"rows": 1, "cols": 2, "figsize": (16, 6)},
            legend={"strategy": "figure", "layout_hint": "spacious"},
        )
    ) as fm_spacious:
        fm_spacious.fig.suptitle(
            'Section 4D: Layout Hints - layout_hint="spacious"', fontsize=16, y=0.95
        )

        fm_spacious.plot(
            "scatter",
            0,
            0,
            hint_data,
            x="performance",
            y="accuracy",
            hue_by="model_size",
            s=60,
            alpha=0.8,
            title="Spacious Layout (y_offset=+0.03)",
        )

        fm_spacious.plot(
            "line",
            0,
            1,
            hint_data.groupby(["model_size", "performance"])
            .agg({"accuracy": "mean"})
            .reset_index(),
            x="performance",
            y="accuracy",
            hue_by="model_size",
            linewidth=2,
            alpha=0.8,
            title="Extra Spacing for Readability",
        )

    show_or_save_plot(fm_spacious.fig, args, "12_legend_showcase_section4d_spacious")

    return [fm_below.fig, fm_side.fig, fm_compact.fig, fm_spacious.fig]


def main(args: Any) -> Any:
    print("Running Legend Positioning Showcase...")

    print("\n=== Section 1A: subplot String Interface ===")
    section_1_subplot_string_interface(args)

    print("\n=== Section 1B: figure String Interface ===")
    section_1_figure_string_interface(args)

    print("\n=== Section 2A: grouped String Interface (Smart Defaults) ===")
    section_2_grouped_string_interface(args)

    print("\n=== Section 2B: none String Interface ===")
    section_2_none_string_interface(args)

    print("\n=== Section 3: PositioningCalculator Integration ===")
    section_3_positioning_calculator_integration(args)

    print("\n=== Section 4: Layout Hints Demonstration ===")
    section_4_layout_hints_demonstration(args)

    print("\nLegend positioning showcase completed successfully!")
    print("Generated 9 comprehensive test figures demonstrating:")
    print("- String interface functionality (subplot, figure, grouped, none)")
    print("- Smart defaults and context-aware features")
    print("- PositioningCalculator integration and responsive behavior")
    print("- Layout hints system (below, side, compact, spacious)")
    return None


if __name__ == "__main__":
    parser = setup_arg_parser(
        description="Legend Positioning Showcase "
        "- Comprehensive Validation of Phase 2 Improvements"
    )
    args = parser.parse_args()
    main(args)
