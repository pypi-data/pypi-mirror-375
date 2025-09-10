from __future__ import annotations

import functools
import sys
from typing import Any, Callable

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from dr_plotter.types import ExpectedChannels, SubplotCoord
from dr_plotter.utils import get_axes_from_grid

from .plot_data_extractor import (
    extract_figure_legend_properties,
    filter_main_grid_axes,
    validate_figure_result,
    validate_legend_properties,
    verify_legend_visibility,
)
from .unified_verification_engine import (
    execute_verification,
    verify_plot_properties_for_subplot,
)
from .verification_formatter import (
    print_critical,
    print_detailed_issues,
    print_failure,
    print_final_success,
    print_info,
    print_item_result,
    print_section_header,
    print_subsection_header,
    print_success,
    print_suggestions,
)

MAX_DISPLAY_ITEMS = 3


def _print_comprehensive_plot_info(ax: Any, subplot_index: int) -> dict[str, Any]:
    info = {
        "title": ax.get_title() or "(no title)",
        "xlabel": ax.get_xlabel() or "(no xlabel)",
        "ylabel": ax.get_ylabel() or "(no ylabel)",
        "lines": [],
        "collections": [],
        "legend": {},
    }

    for i, line in enumerate(ax.lines):
        color = line.get_color()
        normalized_color = mcolors.to_hex(color)
        marker = line.get_marker()
        linewidth = line.get_linewidth()
        linestyle = line.get_linestyle()
        info["lines"].append(
            {
                "index": i,
                "color": normalized_color,
                "marker": str(marker) if marker and marker != "None" else "none",
                "linewidth": linewidth,
                "linestyle": linestyle,
            }
        )

    for i, collection in enumerate(ax.collections):
        try:
            facecolors = collection.get_facecolors()
            if len(facecolors) > 0:
                colors = [mcolors.to_hex(color) for color in facecolors[:5]]
            else:
                colors = ["none"]

            sizes = getattr(collection, "get_sizes", lambda: [1.0])()
            if hasattr(sizes, "__len__") and len(sizes) > 0:
                sample_sizes = list(sizes[:5])
            else:
                sample_sizes = [1.0]

            info["collections"].append(
                {
                    "index": i,
                    "type": type(collection).__name__,
                    "colors": colors,
                    "sizes": sample_sizes,
                }
            )
        except Exception as e:  # noqa: PERF203
            info["collections"].append(
                {
                    "index": i,
                    "type": type(collection).__name__,
                    "error": str(e),
                }
            )

    info["legend"] = validate_legend_properties(ax)
    return info


def _print_failure_message(
    name: str,
    expected: int,
    result: dict[str, Any],
    descriptions: dict[int, str] | None = None,
) -> None:
    print_critical(f"PLOT {name.upper()} FAILED: Legend visibility issues detected!")

    if expected == 0:
        print_info("- Expected NO legends (simple plots with no grouping)", 1)
        print_info(f"- Found {result['visible_legends']} unexpected legend(s)", 1)
    else:
        print_info(f"- Expected {expected} subplot(s) to have visible legends", 1)
        print_info(
            f"- Only {result['visible_legends']} legends are actually visible", 1
        )
        print_info(f"- {result['missing_legends']} legends are missing", 1)

    if descriptions:
        print_info("Expected Configuration:", 1)
        for idx, desc in descriptions.items():
            print_info(f"• Subplot {idx}: {desc}", 2)

    if result.get("issues"):
        print_detailed_issues(result["issues"], 1)

    print_info("This indicates a bug in the legend management system.")
    if expected > 0:
        print_info("The plots should show legends for all visual encoding channels.", 1)
    else:
        print_info(
            "Simple plots without grouping variables should not have legends.", 1
        )
    print_info("Please check the legend manager implementation.", 1)
    print_info("Plot has been saved for visual debugging.", 1)


def verify_plot(  # noqa: C901, PLR0915
    expected_legends: int = 0,
    expected_channels: ExpectedChannels | None = None,
    expected_legend_entries: dict[SubplotCoord, dict[str, int | str]] | None = None,
    verify_legend_consistency: bool = False,
    min_unique_threshold: int = 2,
    tolerance: float | None = None,
    fail_on_missing: bool = True,
    subplot_descriptions: dict[int, str] | None = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:  # noqa: C901, PLR0915
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: C901, PLR0915, PLR0912
            result = func(*args, **kwargs)

            assert isinstance(result, (plt.Figure, list, tuple)), (
                f"Function must return Figure or list/tuple, "
                f"got {type(result).__name__}"
            )

            if isinstance(result, plt.Figure):
                figs = [result]
            elif isinstance(result, (list, tuple)) and len(result) >= 1:
                if all(isinstance(f, plt.Figure) for f in result):
                    figs = list(result)
                elif isinstance(result[0], plt.Figure):
                    figs = [result[0]]
                else:
                    assert False, (
                        f"Function must return Figure(s), got "
                        f"{type(result[0]).__name__} in {type(result).__name__}"
                    )
            else:
                assert False, (
                    f"Function must return Figure or list of Figures, "
                    f"got {type(result).__name__}"
                )

            name = func.__name__.replace("_", "-")
            if name == "main":
                module_parts = func.__module__.split(".") if func.__module__ else []
                name = module_parts[-1] if module_parts else "example"

            fig = figs[0]
            legend_failed = False
            properties_failed = False
            consistency_failed = False

            print_section_header("LEGEND VISIBILITY VERIFICATION")

            if len(figs) == 1:
                verification_result = verify_legend_visibility(
                    fig,
                    expected_visible_count=expected_legends,
                    fail_on_missing=fail_on_missing if expected_legends > 0 else False,
                )

                if not verification_result["success"]:
                    legend_failed = True
                    _print_failure_message(
                        name,
                        expected_legends,
                        verification_result,
                        subplot_descriptions,
                    )
            else:
                print_info(f"Verifying {len(figs)} individual plots...")
                failed_plots = []

                for i, single_fig in enumerate(figs):
                    verification_result = verify_legend_visibility(
                        single_fig,
                        expected_visible_count=expected_legends,
                        fail_on_missing=fail_on_missing
                        if expected_legends > 0
                        else False,
                    )

                    if not verification_result["success"]:
                        failed_plots.append(f"Plot {i + 1}")

                if failed_plots:
                    legend_failed = True
                    print_critical(
                        f"PLOT {name.upper()} FAILED: "
                        f"{len(failed_plots)} plots had legend issues!"
                    )
                    print_info(f"- Failed plots: {', '.join(failed_plots)}", 1)

            if expected_channels:
                print_section_header("PLOT PROPERTIES VERIFICATION")

                all_passed = True
                failed_subplots = []

                for subplot_coord, channels in expected_channels.items():
                    row, col = subplot_coord

                    main_grid_axes = filter_main_grid_axes(fig.axes)
                    ax = get_axes_from_grid(main_grid_axes, row, col)

                    print_subsection_header(
                        f"Verifying subplot [{row},{col}]: {channels}"
                    )

                    subplot_result = verify_plot_properties_for_subplot(
                        ax, channels, min_unique_threshold
                    )

                    print_info(
                        f"Collections found: {subplot_result['collections_found']}"
                    )

                    for channel_result in subplot_result["channels"].values():
                        success = channel_result["passed"]
                        print_item_result(
                            channel_result["channel"],
                            success,
                            channel_result["message"],
                            1,
                        )
                        if (
                            channel_result["passed"]
                            and channel_result["details"]["sample_values"]
                        ):
                            sample = channel_result["details"]["sample_values"]
                            print_info(f"- Sample values: {sample}", 2)

                    if not subplot_result["overall_passed"]:
                        all_passed = False
                        failed_subplots.append(f"[{row},{col}]")
                        print_failure(subplot_result["summary_message"], 1)

                        if subplot_result["suggestions"]:
                            print_suggestions(subplot_result["suggestions"], 2)
                    else:
                        print_success(subplot_result["summary_message"], 1)

                if not all_passed and fail_on_missing:
                    properties_failed = True
                    print_critical("PLOT PROPERTIES VERIFICATION FAILED!")
                    print_info(f"- Failed subplots: {', '.join(failed_subplots)}", 1)
                    print_info(
                        "- This indicates issues with visual encoding channels", 1
                    )
                    print_info("Plot has been saved for visual debugging.", 1)

            if verify_legend_consistency and len(figs) == 1 and expected_channels:
                print_section_header("LEGEND-PLOT CONSISTENCY VERIFICATION")

                if expected_legend_entries:
                    for subplot_coord in expected_legend_entries:
                        row, col = subplot_coord

                        main_grid_axes = filter_main_grid_axes(fig.axes)
                        ax = get_axes_from_grid(main_grid_axes, row, col)

                        assert ax is not None, (
                            f"No axis found at position ({row}, {col})"
                        )

                        print_subsection_header(
                            f"Checking legend consistency for subplot [{row},{col}]"
                        )

                        expected_varying_channels = expected_channels.get(
                            subplot_coord, []
                        )

                        consistency_result = execute_verification(
                            "legend_plot_consistency",
                            {
                                "ax": ax,
                                "expected_varying_channels": expected_varying_channels,
                                "expected_legend_entries": expected_legend_entries.get(
                                    subplot_coord
                                ),
                                "tolerance": tolerance,
                            },
                        )

                        success = consistency_result["overall_passed"]
                        if success:
                            print_success(consistency_result["message"], 1)
                        else:
                            print_failure(consistency_result["message"], 1)

                        for check_result in consistency_result[
                            "consistency_checks"
                        ].values():
                            success = check_result["passed"]
                            if success:
                                print_success(check_result["message"], 2)
                            else:
                                print_failure(check_result["message"], 2)

                        if not consistency_result["overall_passed"]:
                            consistency_failed = True
                            if consistency_result["suggestions"]:
                                print_suggestions(consistency_result["suggestions"], 2)

            failure_types = []
            if properties_failed:
                failure_types.append("plot properties")
            if legend_failed:
                failure_types.append("legend visibility")
            if consistency_failed:
                failure_types.append("legend consistency")

            if failure_types:
                print_critical(f"VERIFICATION FAILED: {' and '.join(failure_types)}")
                sys.exit(1)
            else:
                success_parts = []
                if expected_channels:
                    success_parts.append("Plot properties verified!")

                if expected_legends == 0:
                    success_parts.append("No unexpected legends found - plot is clean!")
                else:
                    success_parts.append(
                        f"All {expected_legends} expected legends verified!"
                    )

                if verify_legend_consistency:
                    success_parts.append("Legend-plot consistency confirmed!")

                print_final_success(f"SUCCESS: {' '.join(success_parts)}")

            return result

        wrapper.__wrapped__ = func
        wrapper._verify_expected = expected_legends  # noqa: SLF001
        wrapper._verify_consistency = verify_legend_consistency  # noqa: SLF001

        return wrapper

    return decorator


def inspect_plot_properties() -> Callable:  # noqa: C901
    def decorator(func: Callable) -> Callable:  # noqa: C901
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: C901, PLR0912
            result = func(*args, **kwargs)

            fig = validate_figure_result(result)

            print_section_header("COMPREHENSIVE PLOT INSPECTION")

            main_grid_axes = filter_main_grid_axes(fig.axes)

            subplot_infos = []
            for i, ax in enumerate(main_grid_axes):
                info = _print_comprehensive_plot_info(ax, i)
                subplot_infos.append(info)

                print_subsection_header(f"Subplot {i}")
                print_info(f'Title: "{info["title"]}"', 1)
                print_info(f'X-label: "{info["xlabel"]}"', 1)
                print_info(f'Y-label: "{info["ylabel"]}"', 1)

                if info["lines"]:
                    print_info("Lines:", 1)
                    for line_info in info["lines"]:
                        details = (
                            f"color={line_info['color']}, "
                            f"marker={line_info['marker']}, "
                            f"width={line_info['linewidth']}, "
                            f"style={line_info['linestyle']}"
                        )
                        print_info(f"Line {line_info['index']}: {details}", 2)

                if info["collections"]:
                    print_info("Collections:", 1)
                    for coll_info in info["collections"]:
                        if "error" in coll_info:
                            print_info(
                                f"{coll_info['type']} {coll_info['index']}: "
                                f"Error - {coll_info['error']}",
                                2,
                            )
                        else:
                            colors_str = ", ".join(
                                coll_info["colors"][:MAX_DISPLAY_ITEMS]
                            ) + (
                                "..."
                                if len(coll_info["colors"]) > MAX_DISPLAY_ITEMS
                                else ""
                            )
                            sizes_str = ", ".join(
                                map(str, coll_info["sizes"][:MAX_DISPLAY_ITEMS])
                            ) + (
                                "..."
                                if len(coll_info["sizes"]) > MAX_DISPLAY_ITEMS
                                else ""
                            )
                            print_info(
                                f"{coll_info['type']} {coll_info['index']}: "
                                f"colors=[{colors_str}], sizes=[{sizes_str}]",
                                2,
                            )

                if not info["lines"] and not info["collections"]:
                    print_info("(no drawable elements found)", 1)

                print_info("Legend:", 1)
                if info["legend"]["visible"]:
                    if info["legend"]["entries"]:
                        for entry in info["legend"]["entries"]:
                            print_info(f'{entry["color"]}: "{entry["label"]}"', 2)
                    else:
                        error_msg = info["legend"].get("error", "unknown error")
                        print_info(
                            f"(legend visible but extraction failed: {error_msg})", 2
                        )
                else:
                    print_info("(no legend found)", 2)

            print_section_header("CONSISTENCY ANALYSIS")

            if subplot_infos:
                line_counts = [len(info["lines"]) for info in subplot_infos]
                if line_counts and len(set(line_counts)) == 1:
                    print_success(
                        f"Line count consistency: "
                        f"All subplots have {line_counts[0]} lines",
                        1,
                    )

                    num_lines = line_counts[0]
                    for pos in range(num_lines):
                        colors_at_pos = [
                            info["lines"][pos]["color"]
                            for info in subplot_infos
                            if len(info["lines"]) > pos
                        ]
                        unique_colors = set(colors_at_pos)

                        if len(unique_colors) == 1:
                            color = next(iter(unique_colors))
                            print_success(
                                f"Line {pos} color: {color} "
                                f"(consistent across {len(colors_at_pos)} subplots)",
                                2,
                            )
                        else:
                            print_info(
                                f"Line {pos} colors: "
                                f"{len(unique_colors)} different colors found",
                                2,
                            )
                            for color in unique_colors:
                                count = colors_at_pos.count(color)
                                print_info(f"  {color}: {count} subplots", 3)
                elif line_counts:
                    print_info(
                        f"Line count variation: "
                        f"{dict(zip(range(len(line_counts)), line_counts))}",
                        1,
                    )

                collection_counts = [len(info["collections"]) for info in subplot_infos]
                if collection_counts and any(count > 0 for count in collection_counts):
                    if len(set(collection_counts)) == 1:
                        print_success(
                            f"Collection count consistency: "
                            f"All subplots have {collection_counts[0]} collections",
                            1,
                        )
                    else:
                        variation_dict = dict(
                            zip(range(len(collection_counts)), collection_counts)
                        )
                        print_info(
                            f"Collection count variation: {variation_dict}",
                            1,
                        )

                legend_states = [info["legend"]["visible"] for info in subplot_infos]
                visible_count = sum(legend_states)
                if visible_count == 0:
                    print_success(
                        "Legend consistency: No legends found (clean plots)", 1
                    )
                elif visible_count == len(subplot_infos):
                    print_success(
                        f"Legend consistency: "
                        f"All {len(subplot_infos)} subplots have legends",
                        1,
                    )
                else:
                    print_info(
                        f"Legend visibility: "
                        f"{visible_count}/{len(subplot_infos)} subplots have legends",
                        1,
                    )
            else:
                print_failure("No subplots found for analysis", 1)

            return result

        return wrapper

    return decorator


def verify_figure_legends(
    expected_legend_count: int,
    legend_strategy: str,
    expected_total_entries: int | None = None,
    expected_channel_entries: dict[str, int] | None = None,
    expected_channels: list[str] | None = None,
    tolerance: float | None = None,
    fail_on_missing: bool = True,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            fig = validate_figure_result(result)

            print_section_header("FIGURE LEGEND VERIFICATION")
            print_info(f"Strategy: {legend_strategy.upper()}")

            figure_props = extract_figure_legend_properties(fig)

            verification_result = execute_verification(
                "figure_legend_strategy",
                {
                    "figure_props": figure_props,
                    "strategy": legend_strategy,
                    "expected_count": expected_legend_count,
                    "expected_total_entries": expected_total_entries,
                    "expected_channel_entries": expected_channel_entries,
                    "expected_channels": expected_channels,
                    "tolerance": tolerance,
                },
            )

            print_info(f"Figure legends found: {figure_props['legend_count']}")
            print_info(f"Expected: {expected_legend_count}")
            success = verification_result["passed"]
            if success:
                print_success(verification_result["message"], 1)
            else:
                print_failure(verification_result["message"], 1)

            for check_result in verification_result["checks"].values():
                success = check_result["passed"]
                if success:
                    print_success(check_result["message"], 1)
                else:
                    print_failure(check_result["message"], 1)

            if not verification_result["passed"] and fail_on_missing:
                print_critical("FIGURE LEGEND VERIFICATION FAILED!")
                print_info(
                    "This indicates issues with figure-level legend management", 1
                )
                sys.exit(1)
            elif verification_result["passed"]:
                print_final_success("SUCCESS: Figure legend verification passed!")

            return result

        return wrapper

    return decorator
