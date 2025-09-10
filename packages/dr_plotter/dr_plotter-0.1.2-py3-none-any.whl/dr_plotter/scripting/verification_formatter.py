from __future__ import annotations

import sys
from typing import Any

import matplotlib.pyplot as plt

LEGEND_CHECK_FAILED = False
LEGEND_CHECK_PASSED = True


class VerificationFormatter:
    SUCCESS_SYMBOL = "✅"
    FAILURE_SYMBOL = "🔴"
    WARNING_SYMBOL = "⚠️"
    INFO_SYMBOL = "🔍"
    DEBUG_SYMBOL = "📊"
    CRITICAL_SYMBOL = "💥"
    SUCCESS_FINAL_SYMBOL = "🎉"

    INDENT_UNIT = "    "
    SECTION_SEPARATOR = "=" * 60
    SUBSECTION_SEPARATOR = "-" * 50

    def __init__(self, output_stream: Any = None) -> None:
        self.output_stream = output_stream or sys.stdout

    def format_section_header(self, title: str, symbol: str = INFO_SYMBOL) -> str:
        return (
            f"\n{self.SECTION_SEPARATOR}\n"
            f"{symbol} {title.upper()}\n{self.SECTION_SEPARATOR}"
        )

    def format_subsection_header(self, title: str) -> str:
        return f"\n{self.DEBUG_SYMBOL} {title}\n{self.SUBSECTION_SEPARATOR}"

    def format_success_message(self, message: str, indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{self.SUCCESS_SYMBOL} {message}"

    def format_failure_message(self, message: str, indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{self.FAILURE_SYMBOL} {message}"

    def format_warning_message(self, message: str, indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{self.WARNING_SYMBOL} {message}"

    def format_critical_message(self, message: str, indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{self.CRITICAL_SYMBOL} {message}"

    def format_final_success_message(self, message: str) -> str:
        return f"\n{self.SUCCESS_FINAL_SYMBOL} {message}"

    def format_info_line(self, message: str, indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{message}"

    def format_summary_stats(self, stats: dict[str, Any], indent_level: int = 0) -> str:
        indent = self.INDENT_UNIT * indent_level
        lines = []
        for key, value in stats.items():
            lines.append(f"{indent}{key}: {value}")
        return "\n".join(lines)

    def format_item_result(
        self, item_name: str, success: bool, message: str, indent_level: int = 0
    ) -> str:
        symbol = self.SUCCESS_SYMBOL if success else self.FAILURE_SYMBOL
        indent = self.INDENT_UNIT * indent_level
        return f"\n{indent}{item_name}: {symbol} {message}"

    def format_suggestions_list(
        self, suggestions: list[str], indent_level: int = 1
    ) -> str:
        if not suggestions:
            return ""

        indent = self.INDENT_UNIT * indent_level
        lines = [f"{indent}Suggestions:"]
        lines.extend([f"{indent}• {suggestion}" for suggestion in suggestions])
        return "\n".join(lines)

    def format_detailed_issues_list(
        self, issues: list[dict[str, Any]], indent_level: int = 1
    ) -> str:
        if not issues:
            return ""

        indent = self.INDENT_UNIT * indent_level
        lines = [f"{indent}Detailed Issues:"]
        for issue in issues:
            subplot = issue.get("subplot", "Unknown")
            reason = issue.get("reason", "No reason provided")
            lines.append(f"{indent}• Subplot {subplot}: {reason}")
        return "\n".join(lines)

    def print_section_header(self, title: str, symbol: str = INFO_SYMBOL) -> None:
        self.output_stream.write(self.format_section_header(title, symbol))
        self.output_stream.flush()

    def print_subsection_header(self, title: str) -> None:
        self.output_stream.write(self.format_subsection_header(title))
        self.output_stream.flush()

    def print_success(self, message: str, indent_level: int = 0) -> None:
        self.output_stream.write(self.format_success_message(message, indent_level))
        self.output_stream.flush()

    def print_failure(self, message: str, indent_level: int = 0) -> None:
        self.output_stream.write(self.format_failure_message(message, indent_level))
        self.output_stream.flush()

    def print_warning(self, message: str, indent_level: int = 0) -> None:
        self.output_stream.write(self.format_warning_message(message, indent_level))
        self.output_stream.flush()

    def print_critical(self, message: str, indent_level: int = 0) -> None:
        self.output_stream.write(self.format_critical_message(message, indent_level))
        self.output_stream.flush()

    def print_final_success(self, message: str) -> None:
        self.output_stream.write(self.format_final_success_message(message))
        self.output_stream.flush()

    def print_info(self, message: str, indent_level: int = 0) -> None:
        self.output_stream.write(self.format_info_line(message, indent_level))
        self.output_stream.flush()

    def print_summary_stats(self, stats: dict[str, Any], indent_level: int = 0) -> None:
        self.output_stream.write(self.format_summary_stats(stats, indent_level))
        self.output_stream.flush()

    def print_item_result(
        self, item_name: str, success: bool, message: str, indent_level: int = 0
    ) -> None:
        self.output_stream.write(
            self.format_item_result(item_name, success, message, indent_level)
        )
        self.output_stream.flush()

    def print_suggestions(self, suggestions: list[str], indent_level: int = 1) -> None:
        formatted = self.format_suggestions_list(suggestions, indent_level)
        if formatted:
            self.output_stream.write(f"\n{formatted}")
            self.output_stream.flush()

    def print_detailed_issues(
        self, issues: list[dict[str, Any]], indent_level: int = 1
    ) -> None:
        formatted = self.format_detailed_issues_list(issues, indent_level)
        if formatted:
            self.output_stream.write(f"\n{formatted}")
            self.output_stream.flush()


_default_formatter = VerificationFormatter()


def get_default_formatter() -> VerificationFormatter:
    return _default_formatter


def set_default_formatter(formatter: VerificationFormatter) -> None:
    global _default_formatter  # noqa: PLW0603
    _default_formatter = formatter


def print_section_header(
    title: str, symbol: str = VerificationFormatter.INFO_SYMBOL
) -> None:
    _default_formatter.print_section_header(title, symbol)


def print_subsection_header(title: str) -> None:
    _default_formatter.print_subsection_header(title)


def print_success(message: str, indent_level: int = 0) -> None:
    _default_formatter.print_success(message, indent_level)


def print_failure(message: str, indent_level: int = 0) -> None:
    _default_formatter.print_failure(message, indent_level)


def print_warning(message: str, indent_level: int = 0) -> None:
    _default_formatter.print_warning(message, indent_level)


def print_critical(message: str, indent_level: int = 0) -> None:
    _default_formatter.print_critical(message, indent_level)


def print_final_success(message: str) -> None:
    _default_formatter.print_final_success(message)


def print_info(message: str, indent_level: int = 0) -> None:
    _default_formatter.print_info(message, indent_level)


def print_summary_stats(stats: dict[str, Any], indent_level: int = 0) -> None:
    _default_formatter.print_summary_stats(stats, indent_level)


def print_item_result(
    item_name: str, success: bool, message: str, indent_level: int = 0
) -> None:
    _default_formatter.print_item_result(item_name, success, message, indent_level)


def print_suggestions(suggestions: list[str], indent_level: int = 1) -> None:
    _default_formatter.print_suggestions(suggestions, indent_level)


def print_detailed_issues(issues: list[dict[str, Any]], indent_level: int = 1) -> None:
    _default_formatter.print_detailed_issues(issues, indent_level)


def verify_legend_visibility_with_formatting(
    figure: plt.Figure,
    expected_visible_count: int | None = None,
    fail_on_missing: bool = True,
) -> dict[str, Any]:
    from .plot_data_extractor import verify_legend_visibility_core

    summary = verify_legend_visibility_core(figure, expected_visible_count)

    results = summary["details"]
    visible_count = summary["visible_legends"]
    total_count = summary["total_subplots"]

    print_section_header("LEGEND VISIBILITY VERIFICATION")
    print_info(f"Total subplots: {total_count}")
    print_info(f"Legends visible: {visible_count}")
    if expected_visible_count is not None:
        print_info(f"Expected visible: {expected_visible_count}")
    print_info(f"Legends missing: {total_count - visible_count}")

    for i, result in results.items():
        if expected_visible_count is not None and expected_visible_count == 0:
            if result["visible"]:
                print_item_result(
                    f"Subplot {i}", LEGEND_CHECK_FAILED, "Unexpected legend found", 1
                )
            else:
                print_item_result(
                    f"Subplot {i}", LEGEND_CHECK_PASSED, "No legend (expected)", 1
                )
        else:
            print_item_result(f"Subplot {i}", result["visible"], result["reason"], 1)

    if expected_visible_count is not None:
        if visible_count != expected_visible_count:
            if expected_visible_count == 0:
                print_failure(
                    f"EXPECTED no legends, but found {visible_count} "
                    f"unexpected legend(s)"
                )
            else:
                print_failure(
                    f"EXPECTED {expected_visible_count} visible legends, "
                    f"but found {visible_count}"
                )
        elif expected_visible_count == 0:
            print_success("EXPECTED no legends and found none - perfect!")
        else:
            print_success(
                f"EXPECTED {expected_visible_count} legends and found "
                f"{visible_count} - perfect!"
            )
    elif visible_count == 0:
        if not fail_on_missing:
            print_success("No legends found (not treated as failure)")
        else:
            summary["success"] = False
            print_critical("CRITICAL: No legends are visible in any subplot!")
    elif visible_count < total_count:
        if fail_on_missing:
            summary["success"] = False
        print_warning(
            f"WARNING: {total_count - visible_count} subplot(s) missing legends"
        )

    if summary["success"]:
        print_success("All legend visibility checks passed!")
    else:
        print_failure("Legend visibility verification FAILED!")

    return summary
