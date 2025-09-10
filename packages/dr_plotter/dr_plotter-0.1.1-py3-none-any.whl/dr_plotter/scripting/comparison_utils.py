from __future__ import annotations

import math

from dr_plotter.types import ColorTuple, ComparisonValue


def values_are_equal(
    a: ComparisonValue,
    b: ComparisonValue,
) -> bool:
    if isinstance(a, str):
        return isinstance(b, str) and a == b

    if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
        return tuples_are_equal(a, b)

    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return floats_are_equal(float(a), float(b))

    if type(a) is not type(b):
        return False

    return a == b


def count_unique_values(values: list[ComparisonValue]) -> set[ComparisonValue]:
    unique = set()
    if not values:
        return unique

    for value in values:
        is_duplicate = False
        for existing in unique:
            if values_are_equal(value, existing):
                is_duplicate = True
                break
        if not is_duplicate:
            unique.add(value)
    return unique


def colors_are_equal(color1: ColorTuple, color2: ColorTuple) -> bool:
    return tuples_are_equal(color1, color2)


def count_unique_floats(values: list[float]) -> set[float]:
    return count_unique_values(values)


def count_unique_colors(values: list[ColorTuple]) -> set[ColorTuple]:
    return count_unique_values(values)


def floats_are_equal(val1: float, val2: float) -> bool:
    if math.isnan(val1) and math.isnan(val2):
        return True
    if math.isnan(val1) or math.isnan(val2):
        return False
    if math.isinf(val1) and math.isinf(val2):
        return val1 == val2
    if math.isinf(val1) or math.isinf(val2):
        return False
    return abs(val1 - val2) < 0


def tuples_are_equal(tuple1: tuple[float, ...], tuple2: tuple[float, ...]) -> bool:
    if len(tuple1) != len(tuple2):
        return False
    return all(floats_are_equal(a, b) for a, b in zip(tuple1, tuple2))
