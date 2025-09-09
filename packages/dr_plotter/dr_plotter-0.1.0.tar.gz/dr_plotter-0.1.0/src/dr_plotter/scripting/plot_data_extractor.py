from __future__ import annotations

from typing import Any

import matplotlib.colors as mcolors
import matplotlib.legend
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.container import BarContainer
from matplotlib.image import AxesImage

from dr_plotter.artist_utils import extract_colors_from_polycollection
from dr_plotter.types import RGBA, CollectionProperties, Position

RGB_CHANNEL_COUNT = 3
RGBA_CHANNEL_COUNT = 4
DEFAULT_LINE_ALPHA = 1.0

LEGEND_CHECK_FAILED = False
LEGEND_CHECK_PASSED = True


def extract_colors(obj: Any) -> list[RGBA]:
    if isinstance(obj, PathCollection):
        return [mcolors.to_rgba(color) for color in obj.get_facecolors()]
    elif isinstance(obj, PolyCollection):
        return extract_colors_from_polycollection(obj)
    elif isinstance(obj, BarContainer):
        return [mcolors.to_rgba(patch.get_facecolor()) for patch in obj.patches]
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_color"):
        colors = []
        for line in obj:
            color = line.get_color()
            alpha = (
                line.get_alpha() if line.get_alpha() is not None else DEFAULT_LINE_ALPHA
            )
            rgba = mcolors.to_rgba(color)
            if len(rgba) == RGB_CHANNEL_COUNT:
                rgba = (*rgba, alpha)
            elif len(rgba) == RGBA_CHANNEL_COUNT:
                rgba = (*rgba[:RGB_CHANNEL_COUNT], alpha)
            colors.append(rgba)
        return colors
    elif hasattr(obj, "get_markerfacecolor"):
        face_color = obj.get_markerfacecolor()
        if (isinstance(face_color, str) and face_color == "none") or face_color is None:
            face_color = obj.get_color()
        return [mcolors.to_rgba(face_color)]
    elif isinstance(obj, AxesImage):
        cmap = obj.get_cmap()
        return [mcolors.to_rgba(cmap(0.5))]
    elif hasattr(obj, "get_facecolor"):
        return [mcolors.to_rgba(obj.get_facecolor())]
    elif hasattr(obj, "get_color"):
        return [mcolors.to_rgba(obj.get_color())]
    else:
        assert False, (
            f"Cannot extract colors from object type {type(obj)} - "
            f"unsupported matplotlib object"
        )


def extract_markers(obj: Any) -> list[str]:
    if isinstance(obj, PathCollection):
        paths = obj.get_paths()
        markers = []
        for path in paths:
            marker_type = _identify_marker_from_path(path)
            markers.append(marker_type)
        return markers
    elif isinstance(obj, PolyCollection):
        return ["violin"]
    elif isinstance(obj, BarContainer):
        return ["bar"] * len(obj.patches)
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_marker"):
        markers = []
        for line in obj:
            marker = line.get_marker()
            if marker is None or marker == "None":
                marker = ""
            markers.append(str(marker))
        return markers
    elif isinstance(obj, AxesImage):
        return ["none"]
    elif hasattr(obj, "get_marker"):
        marker = obj.get_marker()
        return [str(marker) if marker and marker != "None" else "None"]
    else:
        assert False, (
            f"Cannot extract markers from object type {type(obj)} - "
            f"unsupported matplotlib object"
        )


def extract_sizes(obj: Any) -> list[float]:
    if isinstance(obj, PathCollection):
        sizes = obj.get_sizes()
        return [float(size) for size in sizes]
    elif isinstance(obj, PolyCollection):
        return [1.0]
    elif isinstance(obj, BarContainer):
        return [1.0] * len(obj.patches)
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_markersize"):
        return [float(line.get_markersize()) for line in obj]
    elif isinstance(obj, AxesImage):
        return [1.0]
    elif hasattr(obj, "get_markersize"):
        return [float(obj.get_markersize())]
    else:
        assert False, (
            f"Cannot extract sizes from object type {type(obj)} - "
            f"unsupported matplotlib object"
        )


def extract_positions(obj: Any) -> list[Position]:
    if isinstance(obj, PathCollection):
        offsets = obj.get_offsets()
        return [(float(x), float(y)) for x, y in offsets]
    else:
        return []


def extract_alphas(obj: Any) -> list[float]:
    if isinstance(obj, PathCollection):
        facecolors = obj.get_facecolors()
        return [
            float(color[3]) if len(color) >= RGBA_CHANNEL_COUNT else DEFAULT_LINE_ALPHA
            for color in facecolors
        ]
    elif isinstance(obj, PolyCollection):
        alpha = obj.get_alpha()
        if alpha is None:
            facecolors = obj.get_facecolors()
            assert len(facecolors) > 0, (
                "PolyCollection has no facecolors for alpha extraction"
            )
            assert len(facecolors[0]) >= RGBA_CHANNEL_COUNT, (
                "PolyCollection facecolor missing alpha channel"
            )
            return [float(facecolors[0][3])]
        return [float(alpha)]
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_alpha"):
        alphas = []
        for line in obj:
            alpha = line.get_alpha()
            if alpha is None:
                alpha = 1.0  # Matplotlib default when alpha is None
            alphas.append(float(alpha))
        return alphas
    else:
        colors = extract_colors(obj)
        return [
            float(color[3]) if len(color) >= RGBA_CHANNEL_COUNT else DEFAULT_LINE_ALPHA
            for color in colors
        ]


def extract_styles(obj: Any) -> list[str]:
    if isinstance(obj, PolyCollection):
        edgecolors = obj.get_edgecolors()
        linewidths = obj.get_linewidths()
        if len(edgecolors) > 0 and len(linewidths) > 0:
            edge_rgba = mcolors.to_rgba(edgecolors[0])
            if edge_rgba[3] > 0 and linewidths[0] > 0:
                return ["-"]
        return [""]
    elif isinstance(obj, BarContainer):
        return ["-"] * len(obj.patches)
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_linestyle"):
        return [line.get_linestyle() for line in obj]
    elif isinstance(obj, AxesImage):
        return ["-"]
    elif hasattr(obj, "get_linestyle"):
        style = obj.get_linestyle()
        return [str(style) if style is not None else "-"]
    else:
        assert False, (
            f"Cannot extract styles from object type {type(obj)} - "
            f"unsupported matplotlib object"
        )


def extract_legend_properties(ax: Any) -> dict[str, Any]:
    legend = ax.get_legend()
    if legend is None:
        return {
            "handles": [],
            "markers": [],
            "colors": [],
            "sizes": [],
            "labels": [],
            "styles": [],
            "visible": False,
        }

    handles = []
    if hasattr(legend, "legend_handles"):
        handles = legend.legend_handles
    elif hasattr(legend, "legendHandles"):
        handles = legend.legendHandles
    elif hasattr(legend, "get_lines") and hasattr(legend, "get_patches"):
        handles.extend(legend.get_lines())
        handles.extend(legend.get_patches())
    elif hasattr(legend, "_legend_handles"):
        handles = legend._legend_handles  # noqa: SLF001

    return {
        "handles": handles,
        "markers": [_extract_marker_from_handle(h) for h in handles],
        "colors": [_extract_color_from_handle(h) for h in handles],
        "sizes": [_extract_size_from_handle(h) for h in handles],
        "labels": [text.get_text() for text in legend.get_texts()],
        "styles": [_extract_style_from_handle(h) for h in handles],
        "visible": legend.get_visible(),
    }


def extract_collection_properties(
    obj: Any, collection_type: str = "auto"
) -> CollectionProperties:
    if collection_type == "auto":
        collection_type = _detect_collection_type(obj)

    base_props = {
        "type": collection_type,
        "positions": extract_positions(obj),
        "colors": extract_colors(obj),
        "markers": extract_markers(obj),
        "sizes": extract_sizes(obj),
        "alphas": extract_alphas(obj),
        "styles": extract_styles(obj),
    }

    if isinstance(obj, AxesImage):
        base_props.update(_extract_image_properties(obj))

    return base_props


def extract_figure_legend_properties(fig: Any) -> dict[str, Any]:
    legends = [
        child
        for child in fig.get_children()
        if isinstance(child, matplotlib.legend.Legend)
    ]

    result = {
        "legend_count": len(legends),
        "legends": [],
        "total_entries": 0,
    }

    for i, legend in enumerate(legends):
        handles = []
        if hasattr(legend, "legend_handles"):
            handles.extend(legend.legend_handles)
        elif hasattr(legend, "legendHandles"):
            handles.extend(legend.legendHandles)
        elif hasattr(legend, "get_lines") and hasattr(legend, "get_patches"):
            handles.extend(legend.get_lines())
            handles.extend(legend.get_patches())
        elif hasattr(legend, "_legend_handles"):
            handles.extend(legend._legend_handles)  # noqa: SLF001

        legend_props = {
            "index": i,
            "title": legend.get_title().get_text() if legend.get_title() else None,
            "handles": handles,
            "labels": [text.get_text() for text in legend.get_texts()],
            "entry_count": len(legend.get_texts()),
            "ncol": getattr(legend, "_ncols", getattr(legend, "_ncol", 1)),
            "position": getattr(legend, "_loc", None),
            "colors": [_extract_color_from_handle(h) for h in handles],
            "markers": [_extract_marker_from_handle(h) for h in handles],
            "sizes": [_extract_size_from_handle(h) for h in handles],
        }

        result["legends"].append(legend_props)
        result["total_entries"] += legend_props["entry_count"]

    return result


def convert_scatter_size_to_legend_size(scatter_size: float) -> float:
    return np.sqrt(scatter_size / np.pi) * 2


def convert_legend_size_to_scatter_size(legend_size: float) -> float:
    return np.pi * (legend_size / 2) ** 2


def _identify_marker_from_path(path: Any) -> str:
    if not hasattr(path, "vertices"):
        return "unknown"
    marker_by_vertices = {
        1: ".",
        2: "|",
        3: "^",
        4: "D",
        5: "s",
        6: "p",
        10: "o",
    }
    vertices = path.vertices
    return marker_by_vertices.get(len(vertices), f"custom_{len(vertices)}")


def _detect_collection_type(obj: Any) -> str:
    if isinstance(obj, PathCollection):
        return "scatter"
    elif isinstance(obj, PolyCollection):
        return "violin"
    elif isinstance(obj, BarContainer):
        return "bar"
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_marker"):
        return "line"
    elif isinstance(obj, AxesImage):
        return "image"
    else:
        return "unknown"


def _extract_color_from_handle(handle: Any) -> RGBA:
    assert handle is not None, "Handle cannot be None for color extraction"

    if hasattr(handle, "get_markerfacecolor"):
        color = handle.get_markerfacecolor()
        if (isinstance(color, str) and color == "none") or color is None:
            color = handle.get_color()
    elif hasattr(handle, "get_facecolor"):
        color = handle.get_facecolor()
    elif hasattr(handle, "get_color"):
        color = handle.get_color()
    else:
        assert False, (
            f"Handle {type(handle)} does not support color extraction - "
            f"check matplotlib configuration"
        )

    assert color is not None, (
        "Color extraction returned None - matplotlib handle may be invalid"
    )
    return mcolors.to_rgba(color)


def _extract_marker_from_handle(handle: Any) -> str:
    assert handle is not None, "Handle cannot be None for marker extraction"

    if hasattr(handle, "get_marker"):
        marker = handle.get_marker()
        return str(marker) if marker and marker != "None" else "None"
    else:
        return "patch"


def _extract_size_from_handle(handle: Any) -> float:
    assert handle is not None, "Handle cannot be None for size extraction"

    if hasattr(handle, "get_markersize"):
        size = handle.get_markersize()
        assert size is not None, (
            "Marker size extraction returned None - matplotlib handle may be invalid"
        )
        return float(size)
    else:
        return 1.0


def _extract_style_from_handle(handle: Any) -> str:
    assert handle is not None, "Handle cannot be None for style extraction"

    if hasattr(handle, "get_linestyle"):
        style = handle.get_linestyle()
        return str(style) if style is not None else "-"
    else:
        return "-"


def _extract_image_properties(image: AxesImage) -> dict[str, Any]:
    array = image.get_array()
    extent = image.get_extent()
    return {
        "image_data": {
            "shape": array.shape if hasattr(array, "shape") else None,
            "extent": extent,
            "colormap": str(image.get_cmap()),
            "vmin": image.get_clim()[0] if image.get_clim() else None,
            "vmax": image.get_clim()[1] if image.get_clim() else None,
        }
    }


def extract_pathcollections_from_axis(ax: Any) -> list[PathCollection]:
    return [
        collection
        for collection in ax.collections
        if isinstance(collection, PathCollection)
    ]


def extract_polycollections_from_axis(ax: Any) -> list[PolyCollection]:
    return [
        collection
        for collection in ax.collections
        if isinstance(collection, PolyCollection)
    ]


def extract_barcontainers_from_axis(ax: Any) -> list[Any]:
    return [c for c in getattr(ax, "containers", []) if isinstance(c, BarContainer)]


def extract_lines_from_axis(ax: Any) -> list[Any]:
    return [line for line in getattr(ax, "lines", []) if hasattr(line, "get_color")]


def extract_images_from_axis(ax: Any) -> list[AxesImage]:
    return [img for img in getattr(ax, "images", []) if isinstance(img, AxesImage)]


def debug_legend_detection(ax: Any) -> dict[str, Any]:
    legend = ax.get_legend()
    legend_props = extract_legend_properties(ax)

    debug_info = {
        "legend_exists": legend is not None,
        "legend_object": legend,
        "legend_visible": legend_props["visible"],
        "legend_texts": legend_props["labels"],
        "legend_handles": legend_props["handles"],
        "all_legend_children": legend.get_children() if legend else [],
    }

    if legend:
        debug_info["legend_numpoints"] = (
            legend.numpoints if hasattr(legend, "numpoints") else None
        )

    return debug_info


def extract_subplot_properties(ax: Any) -> dict[str, Any]:
    path_collections = extract_pathcollections_from_axis(ax)
    poly_collections = extract_polycollections_from_axis(ax)
    bar_containers = extract_barcontainers_from_axis(ax)
    lines = extract_lines_from_axis(ax)
    images = extract_images_from_axis(ax)
    legend_props = extract_legend_properties(ax)
    legend_debug = debug_legend_detection(ax)

    result = {
        "collections": [],
        "legend": {
            "handles": legend_props["handles"],
            "markers": legend_props["markers"],
            "colors": legend_props["colors"],
            "sizes": legend_props["sizes"],
            "labels": legend_props["labels"],
            "styles": legend_props["styles"],
            "debug": legend_debug,
        },
    }

    for i, collection in enumerate(path_collections):
        collection_props = extract_collection_properties(collection, "scatter")
        collection_props["index"] = i
        result["collections"].append(collection_props)

    for i, collection in enumerate(poly_collections):
        collection_props = extract_collection_properties(collection, "violin")
        collection_props["index"] = len(path_collections) + i
        result["collections"].append(collection_props)

    for i, container in enumerate(bar_containers):
        collection_props = extract_collection_properties(container, "bar")
        collection_props["index"] = len(path_collections) + len(poly_collections) + i
        result["collections"].append(collection_props)

    if lines:
        collection_props = extract_collection_properties(lines, "line")
        collection_props["index"] = (
            len(path_collections) + len(poly_collections) + len(bar_containers)
        )
        result["collections"].append(collection_props)

    for i, image in enumerate(images):
        collection_props = extract_collection_properties(image, "image")
        collection_props["index"] = (
            len(path_collections)
            + len(poly_collections)
            + len(bar_containers)
            + len(lines)
            + i
        )
        result["collections"].append(collection_props)

    return result


def identify_marker_from_path(path: Any) -> str:
    return _identify_marker_from_path(path)


def extract_channel_values_from_collections(
    collections: list[dict[str, Any]], channel: str
) -> list[Any]:
    all_values = []

    if channel == "size":
        for collection in collections:
            all_values.extend(collection["sizes"])
    elif channel in {"hue", "color"}:
        for collection in collections:
            all_values.extend(collection["colors"])
    elif channel == "marker":
        for collection in collections:
            all_values.extend(collection["markers"])
    elif channel == "alpha":
        for collection in collections:
            if collection.get("alphas"):
                all_values.extend(collection["alphas"])
            else:
                for rgba in collection["colors"]:
                    if len(rgba) == RGBA_CHANNEL_COUNT:
                        all_values.append(rgba[3])
                    else:
                        all_values.append(1.0)
    elif channel == "style":
        for collection in collections:
            if "styles" in collection:
                all_values.extend(collection["styles"])

    return all_values


def extract_all_plot_data_from_collections(
    collections: list[dict[str, Any]],
) -> dict[str, list[Any]]:
    all_plot_markers = []
    all_plot_colors = []
    all_plot_sizes = []
    all_plot_alphas = []
    all_plot_styles = []

    for collection in collections:
        all_plot_markers.extend(collection["markers"])
        all_plot_colors.extend(collection["colors"])
        all_plot_sizes.extend(collection["sizes"])

        if collection.get("alphas"):
            all_plot_alphas.extend(collection["alphas"])
        else:
            for rgba_color in collection["colors"]:
                if len(rgba_color) >= RGBA_CHANNEL_COUNT:
                    all_plot_alphas.append(rgba_color[3])
                else:
                    all_plot_alphas.append(1.0)

        if "styles" in collection:
            all_plot_styles.extend(collection["styles"])

    return {
        "markers": all_plot_markers,
        "colors": all_plot_colors,
        "sizes": all_plot_sizes,
        "alphas": all_plot_alphas,
        "styles": all_plot_styles,
    }


def extract_legend_data_with_alphas(
    legend_props: dict[str, Any],
) -> dict[str, list[Any]]:
    legend_alphas = []
    for rgba_color in legend_props["colors"]:
        if len(rgba_color) >= RGBA_CHANNEL_COUNT:
            legend_alphas.append(rgba_color[3])
        else:
            legend_alphas.append(1.0)

    return {
        "markers": legend_props["markers"],
        "colors": legend_props["colors"],
        "sizes": legend_props["sizes"],
        "styles": legend_props["styles"],
        "alphas": legend_alphas,
    }


def validate_legend_properties(ax: plt.Axes) -> dict[str, Any]:
    legend_props = extract_legend_properties(ax)

    if not legend_props["visible"]:
        return {"visible": False, "entries": [], "entry_count": 0}

    legend_colors = legend_props["colors"]
    legend_labels = legend_props["labels"]

    color_label_pairs = []
    for i, (rgba_color, label) in enumerate(zip(legend_colors, legend_labels)):
        hex_color = mcolors.to_hex(rgba_color)
        color_label_pairs.append(
            {
                "index": i,
                "color": hex_color,
                "label": label.strip() if label else "(empty)",
            }
        )

    return {
        "visible": True,
        "entries": color_label_pairs,
        "entry_count": len(legend_labels),
    }


def is_legend_actually_visible(
    ax: plt.Axes, figure: plt.Figure | None = None
) -> dict[str, Any]:
    result = {
        "visible": False,
        "exists": False,
        "marked_visible": False,
        "has_content": False,
        "within_bounds": False,
        "bbox_info": {},
        "reason": "",
    }

    legend = ax.get_legend()
    if legend is None:
        result["reason"] = "No legend object exists"
        return result

    result["exists"] = True

    if not legend.get_visible():
        result["reason"] = "Legend exists but is marked as not visible"
        return result

    result["marked_visible"] = True

    handles = (
        legend.legend_handles
        if hasattr(legend, "legend_handles")
        else legend.get_lines()
    )
    labels = [t.get_text() for t in legend.get_texts()]

    if not handles or not labels or all(not label.strip() for label in labels):
        result["reason"] = "Legend exists and is visible but has no content"
        return result

    result["has_content"] = True

    if figure is None:
        figure = ax.get_figure()

    figure.canvas.draw()

    legend_bbox = legend.get_window_extent()
    fig_bbox = figure.bbox

    result["bbox_info"] = {
        "legend_bbox": {
            "x0": legend_bbox.x0,
            "y0": legend_bbox.y0,
            "x1": legend_bbox.x1,
            "y1": legend_bbox.y1,
            "width": legend_bbox.width,
            "height": legend_bbox.height,
        },
        "figure_bbox": {
            "x0": fig_bbox.x0,
            "y0": fig_bbox.y0,
            "x1": fig_bbox.x1,
            "y1": fig_bbox.y1,
            "width": fig_bbox.width,
            "height": fig_bbox.height,
        },
    }

    legend_in_figure = (
        legend_bbox.x0 < fig_bbox.x1
        and legend_bbox.x1 > fig_bbox.x0
        and legend_bbox.y0 < fig_bbox.y1
        and legend_bbox.y1 > fig_bbox.y0
    )

    if not legend_in_figure:
        result["reason"] = "Legend is positioned outside the visible figure area"
        return result

    if legend_bbox.width <= 0 or legend_bbox.height <= 0:
        result["reason"] = "Legend has zero width or height"
        return result

    result["within_bounds"] = True

    visible_area = min(legend_bbox.x1, fig_bbox.x1) - max(legend_bbox.x0, fig_bbox.x0)
    visible_area *= min(legend_bbox.y1, fig_bbox.y1) - max(legend_bbox.y0, fig_bbox.y0)
    legend_area = legend_bbox.width * legend_bbox.height

    if legend_area > 0:
        fully_visible = 1.0
        visibility_ratio = visible_area / legend_area
        result["bbox_info"]["visibility_ratio"] = visibility_ratio

        if visibility_ratio < fully_visible:
            result["reason"] = (
                f"Legend is mostly clipped (only {visibility_ratio:.1%} visible)"
            )
            return result
    result["visible"] = True
    result["reason"] = "Legend is fully visible and properly positioned"

    return result


def check_all_subplot_legends(figure: plt.Figure) -> dict[int, dict[str, Any]]:
    results = {}

    if hasattr(figure, "axes"):
        for i, ax in enumerate(figure.axes):
            results[i] = is_legend_actually_visible(ax, figure)

    return results


def verify_legend_visibility(  # noqa: PLR0912, C901
    figure: plt.Figure,
    expected_visible_count: int | None = None,
    fail_on_missing: bool = True,
) -> dict[str, Any]:
    from .verification_formatter import (
        print_critical,
        print_failure,
        print_info,
        print_item_result,
        print_section_header,
        print_success,
        print_warning,
    )

    results = check_all_subplot_legends(figure)

    visible_count = sum(1 for result in results.values() if result["visible"])
    total_count = len(results)

    summary = {
        "total_subplots": total_count,
        "visible_legends": visible_count,
        "missing_legends": total_count - visible_count,
        "success": True,
        "issues": [],
        "details": results,
    }

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

        if not result["visible"] and expected_visible_count != 0:
            summary["issues"].append(
                {
                    "subplot": i,
                    "reason": result["reason"],
                    "exists": result["exists"],
                    "marked_visible": result["marked_visible"],
                    "has_content": result["has_content"],
                }
            )
        elif result["visible"] and expected_visible_count == 0:
            summary["issues"].append(
                {
                    "subplot": i,
                    "reason": "Unexpected legend found",
                    "exists": result["exists"],
                    "marked_visible": result["marked_visible"],
                    "has_content": result["has_content"],
                }
            )

    if expected_visible_count is not None:
        if visible_count != expected_visible_count:
            summary["success"] = False
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


def verify_legend_visibility_core(
    figure: plt.Figure, expected_visible_count: int | None = None
) -> dict[str, Any]:
    results = check_all_subplot_legends(figure)

    visible_count = sum(1 for result in results.values() if result["visible"])
    total_count = len(results)

    summary = {
        "total_subplots": total_count,
        "visible_legends": visible_count,
        "missing_legends": total_count - visible_count,
        "success": True,
        "issues": [],
        "details": results,
    }

    for i, result in results.items():
        if not result["visible"] and expected_visible_count != 0:
            summary["issues"].append(
                {
                    "subplot": i,
                    "reason": result["reason"],
                    "exists": result["exists"],
                    "marked_visible": result["marked_visible"],
                    "has_content": result["has_content"],
                }
            )
        elif result["visible"] and expected_visible_count == 0:
            summary["issues"].append(
                {
                    "subplot": i,
                    "reason": "Unexpected legend found",
                    "exists": result["exists"],
                    "marked_visible": result["marked_visible"],
                    "has_content": result["has_content"],
                }
            )

    if (expected_visible_count is not None) and (expected_visible_count != 0):
        summary["success"] = False
    return summary


def filter_main_grid_axes(fig_axes: list[Any]) -> list[Any]:
    grid_axes = []
    main_gridspec = None

    for ax in fig_axes:
        if hasattr(ax, "get_gridspec") and ax.get_gridspec() is not None:
            gs = ax.get_gridspec()
            if main_gridspec is None:
                main_gridspec = gs
            if gs is main_gridspec:
                grid_axes.append(ax)

    return grid_axes


def get_main_grid_axes_from_figure(fig: plt.Figure) -> list[Any]:
    return [
        ax
        for ax in fig.axes
        if hasattr(ax, "get_gridspec") and ax.get_gridspec() is not None
    ]


def validate_subplot_coord_access(
    fig: plt.Figure, subplot_coord: tuple[int, int]
) -> plt.Axes:
    from dr_plotter.utils import get_axes_from_grid

    row, col = subplot_coord
    main_grid_axes = get_main_grid_axes_from_figure(fig)
    assert len(main_grid_axes) > 0, "No main grid axes found in figure"
    ax = get_axes_from_grid(main_grid_axes, row, col)
    assert ax is not None, f"No axis found at position ({row}, {col})"
    return ax


def validate_figure_result(result: Any) -> plt.Figure:
    assert isinstance(result, (plt.Figure, list, tuple)), (
        f"Function must return Figure or list/tuple, got {type(result).__name__}"
    )

    if isinstance(result, plt.Figure):
        return result
    elif isinstance(result, (list, tuple)) and len(result) >= 1:
        assert isinstance(result[0], plt.Figure), (
            f"Function must return Figure(s), got {type(result[0]).__name__}"
        )
        return result[0]
    else:
        assert False, f"Invalid return type: {type(result).__name__}"


def validate_figure_list_result(result: Any) -> list[plt.Figure]:
    assert isinstance(result, (plt.Figure, list, tuple)), (
        f"Function must return Figure or list/tuple, got {type(result).__name__}"
    )

    if isinstance(result, plt.Figure):
        return [result]
    elif isinstance(result, (list, tuple)) and len(result) >= 1:
        if all(isinstance(f, plt.Figure) for f in result):
            return list(result)
        elif isinstance(result[0], plt.Figure):
            return [result[0]]
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


def validate_axes_access(fig_axes: list[Any], row: int, col: int) -> plt.Axes:
    from dr_plotter.utils import get_axes_from_grid

    assert len(fig_axes) > 0, "No axes found in figure"
    ax = get_axes_from_grid(fig_axes, row, col)
    assert ax is not None, f"No axis found at position ({row}, {col})"
    return ax
