from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

import matplotlib.colors as mcolors

from dr_plotter.types import VerificationParams, VerificationResult

from .comparison_utils import (
    count_unique_colors,
    count_unique_floats,
)
from .plot_data_extractor import (
    convert_legend_size_to_scatter_size,
    extract_all_plot_data_from_collections,
    extract_channel_values_from_collections,
    extract_legend_data_with_alphas,
    extract_subplot_properties,
)

MIN_RGB_TUPLE_LENGTH = 3
RANGE_OVERLAP_THRESHOLD = 0.5


class VerificationRule(Protocol):
    def execute(self, params: VerificationParams) -> VerificationResult: ...


class VerificationEngine:
    def __init__(self) -> None:
        self._rules: dict[str, VerificationRule] = {}
        self._register_standard_rules()

    def register_rule(self, name: str, rule: VerificationRule) -> None:
        self._rules[name] = rule

    def execute_verification(
        self, rule_name: str, params: VerificationParams
    ) -> VerificationResult:
        assert rule_name in self._rules, f"Unknown verification rule: {rule_name}"
        return self._rules[rule_name].execute(params)

    def _register_standard_rules(self) -> None:
        self.register_rule("channel_variation", ChannelVariationRule())
        self.register_rule("channel_uniformity", ChannelUniformityRule())
        self.register_rule("consistency_check", ConsistencyCheckRule())
        self.register_rule("legend_plot_consistency", LegendPlotConsistencyRule())
        self.register_rule("figure_legend_strategy", FigureLegendStrategyRule())


class BaseVerificationRule(ABC):
    @abstractmethod
    def execute(self, params: VerificationParams) -> VerificationResult:
        pass

    def _format_sample_values(self, values: list[Any], max_count: int = 5) -> list[Any]:
        limited_values = values[:max_count] if len(values) > max_count else values
        formatted_values = []

        for value in limited_values:
            if isinstance(value, (tuple, list)) and len(value) >= MIN_RGB_TUPLE_LENGTH:
                if all(isinstance(x, float) for x in value):
                    formatted_values.append(tuple(round(x, 3) for x in value))
                else:
                    formatted_values.append(value)
            elif isinstance(value, float):
                formatted_values.append(round(value, 3))
            else:
                formatted_values.append(value)

        return formatted_values


class ChannelVariationRule(BaseVerificationRule):
    def execute(self, params: VerificationParams) -> VerificationResult:
        collections = params["collections"]
        channel = params["channel"]
        min_unique_threshold = params.get("min_unique_threshold", 2)

        result = {
            "channel": channel,
            "passed": False,
            "unique_values": 0,
            "total_points": 0,
            "details": {},
            "message": "",
        }

        if not collections:
            result["message"] = f"No collections found to verify {channel} variation"
            return result

        all_values = extract_channel_values_from_collections(collections, channel)

        if channel == "unknown":
            result["message"] = "Unknown channel: "
            f"{channel}"
            return result

        unique_values = self._count_unique_values(all_values, channel)

        result["unique_values"] = len(unique_values)
        result["total_points"] = len(all_values)

        raw_samples = (
            list(unique_values)[:5]
            if isinstance(unique_values, (set, list))
            else sorted(unique_values)[:5]
        )
        result["details"]["sample_values"] = self._format_sample_values(raw_samples)
        result["passed"] = len(unique_values) >= min_unique_threshold

        if result["passed"]:
            result["message"] = (
                f"{channel.title()} variation: "
                f"PASS ({len(unique_values)} unique values found)"
            )
        else:
            result["message"] = (
                f"{channel.title()} variation: "
                f"FAIL (only {len(unique_values)} unique values, "
                f"expected ≥{min_unique_threshold})"
            )

            if len(unique_values) == 1:
                sample_val = next(iter(unique_values)) if unique_values else "none"
                result["message"] += f"\n   - All points have {channel}: "
            f"{sample_val}"

        return result

    def _count_unique_values(
        self, all_values: list[Any], channel: str
    ) -> set[Any] | list[Any]:
        if channel in ["size", "alpha"]:
            return count_unique_floats(all_values)
        elif channel in ["hue", "color"]:
            return count_unique_colors(all_values)
        else:
            return set(all_values)


class ChannelUniformityRule(BaseVerificationRule):
    def execute(self, params: VerificationParams) -> VerificationResult:
        values = params["values"]
        channel = params["channel"]

        result = {
            "channel": channel,
            "passed": False,
            "unique_values": 0,
            "message": "",
            "uniform_value": None,
        }

        if not values:
            result["message"] = f"{channel.title()} uniformity: "
            "No values to check"
            return result

        unique_values = self._count_unique_values(values, channel)

        result["unique_values"] = len(unique_values)
        result["passed"] = len(unique_values) == 1

        if result["passed"]:
            result["uniform_value"] = (
                next(iter(unique_values)) if unique_values else None
            )
            result["message"] = (
                f"{channel.title()} uniformity: "
                f"PASS (all plot values are {result['uniform_value']})"
            )
        else:
            result["message"] = (
                f"{channel.title()} uniformity: "
                f"FAIL ({len(unique_values)} different plot values found)"
            )
            raw_samples = (
                list(unique_values)[:3]
                if isinstance(unique_values, (set, list))
                else sorted(unique_values)[:3]
            )
            formatted_samples = self._format_sample_values(raw_samples, max_count=3)
            result["message"] += "\n   - Plot sample values: "
            f"{formatted_samples}"

        return result

    def _count_unique_values(
        self, values: list[Any], channel: str
    ) -> set[Any] | list[Any]:
        if channel in ["size", "alpha"]:
            return count_unique_floats(values)
        elif channel in ["hue", "color"]:
            return count_unique_colors(values)
        else:
            return set(values)


class ConsistencyCheckRule(BaseVerificationRule):
    def execute(self, params: VerificationParams) -> VerificationResult:
        channel = params["channel"]
        plot_data = params["plot_data"]
        legend_data = params["legend_data"]
        expected_unique = params.get("expected_unique")

        if channel == "marker":
            return self._verify_marker_consistency(
                plot_data, legend_data, expected_unique
            )
        elif channel in {"color", "hue"}:
            return self._verify_color_consistency(plot_data, legend_data)
        elif channel == "alpha":
            return self._verify_alpha_consistency(plot_data, legend_data)
        elif channel == "size":
            return self._verify_size_consistency(plot_data, legend_data)
        elif channel == "style":
            return self._verify_style_consistency(
                plot_data, legend_data, expected_unique
            )
        else:
            return {"passed": False, "message": f"Unknown channel: {channel}"}

    def _verify_marker_consistency(
        self,
        plot_markers: list[str],
        legend_markers: list[str],
        expected_unique_markers: int | None = None,
    ) -> VerificationResult:
        plot_unique = set(plot_markers)
        legend_unique = set(legend_markers)

        result = {
            "passed": plot_unique == legend_unique,
            "plot_markers": sorted(plot_unique),
            "legend_markers": sorted(legend_unique),
            "missing_from_legend": sorted(plot_unique - legend_unique),
            "extra_in_legend": sorted(legend_unique - plot_unique),
            "message": "",
        }

        if expected_unique_markers and len(plot_unique) != expected_unique_markers:
            result["passed"] = False
            result["message"] = (
                f"Expected {expected_unique_markers} unique markers in plot, "
                f"found {len(plot_unique)}"
            )
            return result

        if result["passed"]:
            result["message"] = (
                f"Marker consistency: PASS ({len(plot_unique)} unique markers match)"
            )
        else:
            result["message"] = "Marker consistency: FAIL"
            if result["missing_from_legend"]:
                result["message"] += (
                    f"\n   - Missing from legend: {result['missing_from_legend']}"
                )
            if result["extra_in_legend"]:
                result["message"] += (
                    f"\n   - Extra in legend: {result['extra_in_legend']}"
                )

        return result

    def _verify_color_consistency(
        self,
        plot_colors: list[tuple[float, ...]],
        legend_colors: list[tuple[float, ...]],
    ) -> VerificationResult:
        plot_unique = count_unique_colors(plot_colors)
        legend_unique = count_unique_colors(legend_colors)

        plot_hex = [mcolors.to_hex(color) for color in plot_unique]
        legend_hex = [mcolors.to_hex(color) for color in legend_unique]

        result = {
            "passed": set(plot_hex) == set(legend_hex),
            "plot_colors": sorted(plot_hex),
            "legend_colors": sorted(legend_hex),
            "message": "",
        }

        if result["passed"]:
            result["message"] = (
                f"Color consistency: PASS ({len(plot_unique)} unique colors match)"
            )
        else:
            result["message"] = "Color consistency: FAIL"
            result["message"] += "\n   - Plot colors: "
            f"{result['plot_colors']}"
            result["message"] += "\n   - Legend colors: "
            f"{result['legend_colors']}"

        return result

    def _verify_alpha_consistency(
        self,
        plot_alphas: list[float],
        legend_alphas: list[float],
    ) -> VerificationResult:
        plot_unique = count_unique_floats(plot_alphas)
        legend_unique = count_unique_floats(legend_alphas)

        result = {
            "passed": len(plot_unique) == len(legend_unique),
            "plot_alpha_range": (min(plot_unique), max(plot_unique))
            if plot_unique
            else (1.0, 1.0),
            "legend_alpha_range": (min(legend_unique), max(legend_unique))
            if legend_unique
            else (1.0, 1.0),
            "plot_unique_count": len(plot_unique),
            "legend_unique_count": len(legend_unique),
            "message": "",
        }

        if plot_unique and legend_unique:
            plot_min, plot_max = min(plot_unique), max(plot_unique)
            legend_min, legend_max = min(legend_unique), max(legend_unique)

            range_overlap = (
                min(plot_max, legend_max) - max(plot_min, legend_min)
            ) / max((plot_max - plot_min), 0.1)

            if range_overlap > RANGE_OVERLAP_THRESHOLD:
                result["passed"] = True
                result["message"] = (
                    "Alpha consistency: PASS (ranges overlap sufficiently)"
                )
            else:
                result["passed"] = False
                result["message"] = "Alpha consistency: FAIL (ranges don't overlap)"
        elif result["passed"]:
            result["message"] = (
                f"Alpha consistency: PASS ({len(plot_unique)} alpha values match)"
            )
        else:
            result["message"] = "Alpha consistency: FAIL"
            result["message"] += (
                f"\n   - Plot alpha range: {result['plot_alpha_range']}"
            )
            result["message"] += (
                f"\n   - Legend alpha range: {result['legend_alpha_range']}"
            )

        return result

    def _verify_size_consistency(
        self,
        plot_sizes: list[float],
        legend_sizes: list[float],
    ) -> VerificationResult:
        legend_as_scatter = [
            convert_legend_size_to_scatter_size(size) for size in legend_sizes
        ]

        plot_unique = count_unique_floats(plot_sizes)
        legend_unique = count_unique_floats(legend_as_scatter)

        result = {
            "passed": len(plot_unique) == len(legend_unique),
            "plot_size_range": (min(plot_unique), max(plot_unique))
            if plot_unique
            else (0, 0),
            "legend_size_range": (min(legend_unique), max(legend_unique))
            if legend_unique
            else (0, 0),
            "message": "",
        }

        if result["passed"]:
            result["message"] = "Size consistency: PASS"
        else:
            result["message"] = "Size consistency: FAIL"
            result["message"] += "\n   - Plot size range: "
            f"{result['plot_size_range']}"
            result["message"] += (
                f"\n   - Legend size range: {result['legend_size_range']}"
            )

        return result

    def _verify_style_consistency(
        self,
        plot_styles: list[str],
        legend_styles: list[str],
        expected_unique_styles: int | None = None,
    ) -> VerificationResult:
        plot_unique = set(plot_styles)
        legend_unique = set(legend_styles)

        result = {
            "passed": plot_unique == legend_unique,
            "plot_styles": sorted(plot_unique),
            "legend_styles": sorted(legend_unique),
            "missing_from_legend": sorted(plot_unique - legend_unique),
            "extra_in_legend": sorted(legend_unique - plot_unique),
            "message": "",
        }

        if expected_unique_styles and len(plot_unique) != expected_unique_styles:
            result["passed"] = False
            result["message"] = (
                f"Expected {expected_unique_styles} unique styles in plot, "
                f"found {len(plot_unique)}"
            )
            return result

        if result["passed"]:
            result["message"] = (
                f"Style consistency: PASS ({len(plot_unique)} unique styles match)"
            )
        else:
            result["message"] = "Style consistency: FAIL"
            if result["missing_from_legend"]:
                result["message"] += (
                    f"\n   - Missing from legend: {result['missing_from_legend']}"
                )
            if result["extra_in_legend"]:
                result["message"] += (
                    f"\n   - Extra in legend: {result['extra_in_legend']}"
                )

        return result


class LegendPlotConsistencyRule(BaseVerificationRule):
    def execute(self, params: VerificationParams) -> VerificationResult:  # noqa: C901, PLR0912
        ax = params["ax"]
        expected_varying_channels = params.get("expected_varying_channels")
        expected_legend_entries = params.get("expected_legend_entries")

        props = extract_subplot_properties(ax)

        result = {
            "consistency_checks": {},
            "legend_entry_checks": {},
            "overall_passed": True,
            "message": "",
            "suggestions": [],
        }

        all_plot_data = extract_all_plot_data_from_collections(props["collections"])
        legend_data = extract_legend_data_with_alphas(props["legend"])

        if expected_legend_entries:
            for entry_type, expected_count in expected_legend_entries.items():
                if entry_type == "legend_count":
                    actual_count = (
                        len(props["legend"]["labels"])
                        if props["legend"]["labels"]
                        else 0
                    )
                elif entry_type == "hue":
                    actual_count = (
                        len(legend_data["colors"]) if legend_data["colors"] else 0
                    )
                elif entry_type == "marker":
                    actual_count = (
                        len(legend_data["markers"]) if legend_data["markers"] else 0
                    )
                elif entry_type == "alpha":
                    actual_count = (
                        len(legend_data["alphas"]) if legend_data["alphas"] else 0
                    )
                elif entry_type == "size":
                    actual_count = (
                        len(legend_data["sizes"]) if legend_data["sizes"] else 0
                    )
                elif entry_type == "style":
                    actual_count = (
                        len(legend_data["styles"]) if legend_data["styles"] else 0
                    )
                else:
                    continue

                entry_check = {
                    "passed": actual_count == expected_count,
                    "message": f"{entry_type}: "
                    f"expected {expected_count}, got {actual_count}",
                    "expected": expected_count,
                    "actual": actual_count,
                }
                result["legend_entry_checks"][entry_type] = entry_check
                if not entry_check["passed"]:
                    result["overall_passed"] = False

        if expected_varying_channels is None:
            expected_varying_channels = ["hue", "marker", "alpha", "size", "style"]

        channel_mapping = {
            "marker": (all_plot_data["markers"], legend_data["markers"]),
            "hue": (all_plot_data["colors"], legend_data["colors"]),
            "alpha": (all_plot_data["alphas"], legend_data["alphas"]),
            "size": (all_plot_data["sizes"], legend_data["sizes"]),
            "style": (all_plot_data["styles"], legend_data["styles"]),
        }

        for channel in ["marker", "hue", "alpha", "size", "style"]:
            if channel not in channel_mapping or not channel_mapping[channel][0]:
                continue

            plot_data, legend_data_for_channel = channel_mapping[channel]
            should_vary = channel in expected_varying_channels or (
                channel == "hue" and "color" in expected_varying_channels
            )

            if should_vary and legend_data_for_channel:
                consistency_rule = ConsistencyCheckRule()
                consistency_params = {
                    "channel": channel,
                    "plot_data": plot_data,
                    "legend_data": legend_data_for_channel,
                }
                consistency_check = consistency_rule.execute(consistency_params)
                result["consistency_checks"][f"{channel}s"] = consistency_check
                if not consistency_check["passed"]:
                    result["overall_passed"] = False
            elif should_vary and not legend_data_for_channel:
                variation_rule = ChannelVariationRule()
                variation_params = {
                    "collections": [
                        {
                            "colors": all_plot_data["colors"],
                            "markers": all_plot_data["markers"],
                            "sizes": all_plot_data["sizes"],
                        }
                    ],
                    "channel": channel,
                }
                variation_check = variation_rule.execute(variation_params)

                message = (
                    f"{channel.title()} variation: "
                    f"VERIFIED (plot shows expected variation, legend data missing)"
                    if variation_check["passed"]
                    else f"{channel.title()} variation: "
                    f"MISSING (expected variation not found in plot)"
                )

                special_check = {
                    "passed": variation_check["passed"],
                    "message": message,
                }
                result["consistency_checks"][f"{channel}s"] = special_check
                if not special_check["passed"]:
                    result["overall_passed"] = False
            elif not should_vary:
                uniformity_rule = ChannelUniformityRule()
                uniformity_params = {
                    "values": plot_data,
                    "channel": channel,
                }
                uniformity_check = uniformity_rule.execute(uniformity_params)
                result["consistency_checks"][f"{channel}s"] = uniformity_check
                if not uniformity_check["passed"]:
                    result["overall_passed"] = False

        if result["overall_passed"]:
            checks = list(result["consistency_checks"].keys())
            entry_checks = list(result["legend_entry_checks"].keys())
            all_checks = checks + entry_checks
            result["message"] = (
                f"Legend-plot consistency: PASS ({', '.join(all_checks)})"
            )
        else:
            failed_consistency = [
                k for k, v in result["consistency_checks"].items() if not v["passed"]
            ]
            failed_entries = [
                k for k, v in result["legend_entry_checks"].items() if not v["passed"]
            ]
            all_failed = failed_consistency + failed_entries
            result["message"] = (
                f"Legend-plot consistency: FAIL ({', '.join(all_failed)})"
            )
            result["suggestions"].append("Check legend proxy artist creation")
            result["suggestions"].append(
                "Verify legend manager is creating correct entries"
            )

        return result


class FigureLegendStrategyRule(BaseVerificationRule):
    def execute(self, params: VerificationParams) -> VerificationResult:
        figure_props = params["figure_props"]
        strategy = params["strategy"]
        expected_count = params["expected_count"]
        expected_total_entries = params.get("expected_total_entries")
        expected_channel_entries = params.get("expected_channel_entries")
        expected_channels = params.get("expected_channels")

        result = {
            "passed": True,
            "strategy": strategy,
            "checks": {},
            "message": "",
        }

        count_check = {
            "passed": figure_props["legend_count"] == expected_count,
            "expected": expected_count,
            "actual": figure_props["legend_count"],
            "message": "",
        }

        if count_check["passed"]:
            count_check["message"] = (
                f"Legend count: PASS ({expected_count} legends found)"
            )
        else:
            count_check["message"] = (
                f"Legend count: "
                f"FAIL (expected {expected_count}, got {figure_props['legend_count']})"
            )
            result["passed"] = False

        result["checks"]["legend_count"] = count_check

        if strategy == "figure_below":
            return self._verify_unified_figure_strategy(
                figure_props,
                expected_total_entries,
                result,
            )
        elif strategy == "split":
            return self._verify_split_figure_strategy(
                figure_props,
                expected_channel_entries,
                expected_channels,
                result,
            )
        else:
            result["passed"] = False
            result["message"] = "Unknown strategy: "
            f"{strategy}"
            return result

    def _verify_unified_figure_strategy(
        self,
        figure_props: dict[str, Any],
        expected_total_entries: int | None,
        result: dict[str, Any],
    ) -> VerificationResult:
        if not result["checks"]["legend_count"]["passed"]:
            result["message"] = "Cannot verify unified legend - wrong legend count"
            return result

        legend = figure_props["legends"][0]

        if expected_total_entries is not None:
            entries_check = {
                "passed": legend["entry_count"] == expected_total_entries,
                "expected": expected_total_entries,
                "actual": legend["entry_count"],
                "message": "",
            }

            if entries_check["passed"]:
                entries_check["message"] = (
                    f"Entry count: PASS ({expected_total_entries} entries)"
                )
            else:
                entries_check["message"] = (
                    f"Entry count: "
                    f"FAIL (expected {expected_total_entries}, "
                    f"got {legend['entry_count']})"
                )
                result["passed"] = False

            result["checks"]["entry_count"] = entries_check

        title_check = {
            "passed": legend["title"] is None or legend["title"] == "",
            "message": "No channel title: PASS (unified legend)"
            if (legend["title"] is None or legend["title"] == "")
            else f"Unexpected title: {legend['title']}",
        }

        result["checks"]["unified_title"] = title_check
        if not title_check["passed"]:
            result["passed"] = False

        result["message"] = (
            "Unified figure legend verified"
            if result["passed"]
            else "Unified figure legend verification failed"
        )
        return result

    def _verify_split_figure_strategy(
        self,
        figure_props: dict[str, Any],
        expected_channel_entries: dict[str, int] | None,
        expected_channels: list[str] | None,
        result: dict[str, Any],
    ) -> VerificationResult:
        if not result["checks"]["legend_count"]["passed"]:
            result["message"] = "Cannot verify split legends - wrong legend count"
            return result

        found_channels = [
            legend["title"].lower()
            for legend in figure_props["legends"]
            if legend["title"]
        ]

        if expected_channels:
            expected_set = {ch.lower() for ch in expected_channels}
            found_set = set(found_channels)

            channels_check = {
                "passed": expected_set == found_set,
                "expected": sorted(expected_set),
                "found": sorted(found_set),
                "message": "",
            }

            if channels_check["passed"]:
                channels_check["message"] = (
                    f"Channel coverage: PASS ({len(expected_set)} channels)"
                )
            else:
                missing = expected_set - found_set
                extra = found_set - expected_set
                channels_check["message"] = "Channel coverage: FAIL"
                if missing:
                    channels_check["message"] += f" (missing: {sorted(missing)})"
                if extra:
                    channels_check["message"] += f" (extra: {sorted(extra)})"
                result["passed"] = False

            result["checks"]["channel_coverage"] = channels_check

        if expected_channel_entries:
            for legend in figure_props["legends"]:
                channel = legend["title"].lower() if legend["title"] else "untitled"
                if channel in expected_channel_entries:
                    expected_entries = expected_channel_entries[channel]
                    entries_check = {
                        "passed": legend["entry_count"] == expected_entries,
                        "expected": expected_entries,
                        "actual": legend["entry_count"],
                        "message": f"{channel.title()} entries: "
                        f"PASS ({expected_entries})"
                        if legend["entry_count"] == expected_entries
                        else f"{channel.title()} entries: "
                        f"FAIL (expected {expected_entries}, "
                        f"got {legend['entry_count']})",
                    }

                    result["checks"][f"{channel}_entries"] = entries_check
                    if not entries_check["passed"]:
                        result["passed"] = False

        result["message"] = (
            "Split figure legends verified"
            if result["passed"]
            else "Split figure legend verification failed"
        )
        return result


_default_engine = VerificationEngine()


def execute_verification(
    rule_name: str, params: VerificationParams
) -> VerificationResult:
    return _default_engine.execute_verification(rule_name, params)


def register_verification_rule(name: str, rule: VerificationRule) -> None:
    _default_engine.register_rule(name, rule)


def verify_plot_properties_for_subplot(
    ax: Any,
    expected_channels: list[str],
    min_unique_threshold: int = 2,
) -> dict[str, Any]:
    props = extract_subplot_properties(ax)

    result = {
        "subplot_coord": getattr(ax, "_subplot_spec", "unknown"),
        "collections_found": len(props["collections"]),
        "channels": {},
        "overall_passed": True,
        "summary_message": "",
        "suggestions": [],
    }

    if not props["collections"]:
        result["overall_passed"] = False
        result["summary_message"] = "No collections found in subplot"
        result["suggestions"].append("Check if plot was created successfully")
        return result

    passed_channels = []
    failed_channels = []

    for channel in expected_channels:
        channel_result = execute_verification(
            "channel_variation",
            {
                "collections": props["collections"],
                "channel": channel,
                "min_unique_threshold": min_unique_threshold,
            },
        )
        result["channels"][channel] = channel_result

        if channel_result["passed"]:
            passed_channels.append(channel)
        else:
            failed_channels.append(channel)

    result["overall_passed"] = len(failed_channels) == 0

    if result["overall_passed"]:
        result["summary_message"] = (
            f"All channels verified: {', '.join(passed_channels)}"
        )
    else:
        result["summary_message"] = (
            f"Channel verification failed: {', '.join(failed_channels)}"
        )

        for channel in failed_channels:
            if channel == "size":
                result["suggestions"].append(
                    "Check if size_by parameter is properly configured"
                )
            elif channel in ["hue", "color"]:
                result["suggestions"].append(
                    "Check if hue_by parameter creates color variation"
                )
            elif channel == "marker":
                result["suggestions"].append(
                    "Check if marker_by parameter creates marker variation"
                )
            elif channel == "alpha":
                result["suggestions"].append(
                    "Check if alpha_by parameter creates alpha variation"
                )

    return result
