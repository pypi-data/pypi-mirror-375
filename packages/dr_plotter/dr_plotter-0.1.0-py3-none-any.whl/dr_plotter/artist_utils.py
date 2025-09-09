import matplotlib.colors as mcolors
from matplotlib.collections import PolyCollection

from dr_plotter.types import RGBA

DEFAULT_ALPHA_VALUE = 1.0


def extract_facecolor_from_polycollection(obj: PolyCollection) -> RGBA:
    facecolors = obj.get_facecolors()
    assert len(facecolors) > 0, "PolyCollection has no facecolors"
    return mcolors.to_rgba(facecolors[0])


def extract_edgecolor_from_polycollection(obj: PolyCollection) -> RGBA:
    edgecolors = obj.get_edgecolors()
    assert len(edgecolors) > 0, "PolyCollection has no edgecolors"
    return mcolors.to_rgba(edgecolors[0])


def extract_alpha_from_artist(obj: PolyCollection) -> float:
    alpha = obj.get_alpha()
    return float(alpha) if alpha is not None else DEFAULT_ALPHA_VALUE


def extract_colors_from_polycollection(obj: PolyCollection) -> list[RGBA]:
    facecolors = obj.get_facecolors()
    assert len(facecolors) > 0, "PolyCollection has no facecolors"
    return [mcolors.to_rgba(color) for color in facecolors]


def extract_single_color_from_polycollection_list(bodies: list[PolyCollection]) -> RGBA:
    assert len(bodies) > 0, "Bodies list cannot be empty"
    return extract_facecolor_from_polycollection(bodies[0])


def extract_single_edgecolor_from_polycollection_list(
    bodies: list[PolyCollection],
) -> RGBA:
    assert len(bodies) > 0, "Bodies list cannot be empty"
    return extract_edgecolor_from_polycollection(bodies[0])


def extract_single_alpha_from_polycollection_list(
    bodies: list[PolyCollection],
) -> float:
    assert len(bodies) > 0, "Bodies list cannot be empty"
    return extract_alpha_from_artist(bodies[0])
