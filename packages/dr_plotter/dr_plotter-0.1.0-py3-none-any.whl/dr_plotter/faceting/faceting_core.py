from __future__ import annotations
from typing import Any, TYPE_CHECKING

import matplotlib.axes
import pandas as pd

from dr_plotter.configs import FacetingConfig
from dr_plotter.legend_manager import LegendEntry
from dr_plotter.styling_utils import apply_grid_styling

if TYPE_CHECKING:
    from dr_plotter.figure_manager import FigureManager
    from dr_plotter.faceting.style_coordination import FacetStyleCoordinator

SUPPORTED_PLOT_TYPES = ["line", "scatter", "bar", "fill_between", "heatmap"]
GRID_SHAPE_DIMENSIONS = 2


def prepare_faceted_subplots(
    data: pd.DataFrame, config: FacetingConfig, grid_shape: tuple[int, int]
) -> dict[tuple[int, int], pd.DataFrame]:
    assert not data.empty, "Cannot facet empty DataFrame"
    assert config.rows or config.cols, "Must specify rows or cols for faceting"
    assert isinstance(grid_shape, tuple) and len(grid_shape) == GRID_SHAPE_DIMENSIONS, (
        "grid_shape must be (rows, cols) tuple"
    )

    rows, cols = grid_shape

    # Check if we're doing targeted plotting at a specific position
    if config.target_row is not None and config.target_col is not None:
        # Validate the target position is within the grid
        assert config.target_row < rows and config.target_col < cols, (
            f"Target position ({config.target_row}, {config.target_col}) "
            f"exceeds grid dimensions {grid_shape}"
        )

        # When targeting a specific position, use all the data for that position
        # This is typically used for highlighting specific cells with filtered data
        subsets = {(config.target_row, config.target_col): data.copy()}
        return subsets

    # Normal faceting behavior
    row_values = _extract_dimension_values(data, config.rows, config.row_order)
    col_values = _extract_dimension_values(data, config.cols, config.col_order)

    subsets = {}

    for r, row_val in enumerate(row_values):
        for c, col_val in enumerate(col_values):
            subset = _create_data_subset(data, config, row_val, col_val)
            if not subset.empty:
                subsets[(r, c)] = subset

    return subsets


def _extract_dimension_values(
    data: pd.DataFrame, column: str | None, order: list[str] | None
) -> list[Any]:
    if not column:
        return [None]

    values = sorted(data[column].unique())
    if order:
        values = [v for v in order if v in values]

    return values


def _create_data_subset(
    data: pd.DataFrame, config: FacetingConfig, row_val: Any, col_val: Any
) -> pd.DataFrame:
    mask = pd.Series([True] * len(data), index=data.index)

    if row_val is not None and config.rows:
        mask = mask & (data[config.rows] == row_val)
    if col_val is not None and config.cols:
        mask = mask & (data[config.cols] == col_val)

    return data[mask].copy()


def plot_faceted_data(
    fm: FigureManager,
    data_subsets: dict[tuple[int, int], pd.DataFrame],
    plot_type: str,
    config: FacetingConfig,
    style_coordinator: FacetStyleCoordinator,
    **kwargs: Any,
) -> None:
    assert data_subsets, "Cannot plot with empty data_subsets"
    assert plot_type in SUPPORTED_PLOT_TYPES, f"Unsupported plot type: {plot_type}"
    assert config.x and config.y, "Must specify x and y columns for plotting"

    # Reconstruct full dataset from subsets for dimension title extraction
    full_data = pd.concat(data_subsets.values(), ignore_index=True)

    for (row, col), subplot_data in data_subsets.items():
        _plot_subplot_at_position(
            fm,
            row,
            col,
            subplot_data,
            plot_type,
            config,
            style_coordinator,
            full_data,
            **kwargs,
        )


def _plot_subplot_at_position(
    fm: FigureManager,
    row: int,
    col: int,
    subplot_data: pd.DataFrame,
    plot_type: str,
    config: FacetingConfig,
    style_coordinator: FacetStyleCoordinator,
    full_data: pd.DataFrame,
    **kwargs: Any,
) -> None:
    if config.lines and config.lines in subplot_data.columns:
        _plot_with_style_coordination(
            fm, row, col, subplot_data, plot_type, config, style_coordinator, **kwargs
        )
    else:
        _plot_single_series_at_position(
            fm, row, col, subplot_data, plot_type, config, **kwargs
        )

    _apply_subplot_customization(fm, row, col, config, full_data)


def _plot_with_style_coordination(
    fm: FigureManager,
    row: int,
    col: int,
    subplot_data: pd.DataFrame,
    plot_type: str,
    config: FacetingConfig,
    style_coordinator: FacetStyleCoordinator,
    **kwargs: Any,
) -> None:
    ax = fm.get_axes(row, col)

    lines_values = _extract_dimension_values(
        subplot_data, config.lines, config.lines_order
    )

    for line_value in lines_values:
        if line_value is None:
            continue

        line_data = subplot_data[subplot_data[config.lines] == line_value]
        assert not line_data.empty, f"Line data for {line_value} is empty"

        plot_kwargs = style_coordinator.get_consistent_style(config.lines, line_value)
        plot_kwargs.update(kwargs)

        artist = _execute_plot_call(ax, plot_type, line_data, config, **plot_kwargs)
        _register_legend_entry_if_needed(
            fm, artist, str(line_value), ax, config.lines, line_value
        )


def _plot_single_series_at_position(
    fm: FigureManager,
    row: int,
    col: int,
    subplot_data: pd.DataFrame,
    plot_type: str,
    config: FacetingConfig,
    **kwargs: Any,
) -> None:
    ax = fm.get_axes(row, col)
    _execute_plot_call(ax, plot_type, subplot_data, config, **kwargs)


def _execute_plot_call(
    ax: matplotlib.axes.Axes,
    plot_type: str,
    data: pd.DataFrame,
    config: FacetingConfig,
    **kwargs: Any,
) -> Any:
    plot_handlers = {
        "line": _plot_line_data,
        "scatter": _plot_scatter_data,
        "bar": _plot_bar_data,
        "fill_between": _plot_fill_between_data,
        "heatmap": _plot_heatmap_data,
    }
    return plot_handlers[plot_type](ax, data, config, **kwargs)


def _plot_line_data(
    ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs: Any
) -> Any:
    lines = ax.plot(data[config.x], data[config.y], **kwargs)
    return lines[0] if lines else None


def _register_legend_entry_if_needed(
    fm: FigureManager,
    artist: Any,
    label: str,
    ax: matplotlib.axes.Axes,
    visual_channel: str,
    channel_value: Any,
) -> None:
    if fm and artist and label:
        entry = LegendEntry(
            artist=artist,
            label=label,
            axis=ax,
            visual_channel=visual_channel,
            channel_value=channel_value,
            source_column=visual_channel,
        )
        fm.register_legend_entry(entry)


def _plot_scatter_data(
    ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs: Any
) -> None:
    ax.scatter(data[config.x], data[config.y], **kwargs)


def _plot_bar_data(
    ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs: Any
) -> None:
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ["marker"]}
    ax.bar(data[config.x], data[config.y], **filtered_kwargs)


def _plot_fill_between_data(
    ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs: Any
) -> None:
    ax.fill_between(data[config.x], data[config.y], **kwargs)


def _plot_heatmap_data(
    ax: matplotlib.axes.Axes, data: pd.DataFrame, config: FacetingConfig, **kwargs: Any
) -> None:
    values = data.pivot_table(index=config.y, columns=config.x, values="value")
    ax.imshow(values, **kwargs)
    ax.set_xticks(range(len(values.columns)))
    ax.set_yticks(range(len(values.index)))
    ax.set_xticklabels(values.columns)
    ax.set_yticklabels(values.index)


def _apply_subplot_customization(
    fm: FigureManager, row: int, col: int, config: FacetingConfig, data: pd.DataFrame
) -> None:
    _apply_axis_labels(fm, row, col, config)
    _apply_exterior_labels(fm, row, col, config, data)
    _apply_axis_limits(fm, row, col, config)
    _apply_dimension_titles(fm, row, col, config, data)
    _apply_grid_styling(fm, row, col)


def _apply_axis_labels(
    fm: FigureManager, row: int, col: int, config: FacetingConfig
) -> None:
    ax = fm.get_axes(row, col)

    if _has_custom_label(config.x_labels, row, col):
        label = config.x_labels[row][col]
        if label is not None:
            ax.set_xlabel(label)

    if _has_custom_label(config.y_labels, row, col):
        label = config.y_labels[row][col]
        if label is not None:
            ax.set_ylabel(label)


def _apply_axis_limits(
    fm: FigureManager, row: int, col: int, config: FacetingConfig
) -> None:
    ax = fm.get_axes(row, col)

    if _has_custom_label(config.xlim, row, col):
        xlim = config.xlim[row][col]
        if xlim is not None:
            ax.set_xlim(xlim)

    if _has_custom_label(config.ylim, row, col):
        ylim = config.ylim[row][col]
        if ylim is not None:
            ax.set_ylim(ylim)


def _has_custom_label(labels: list[list[Any]] | None, row: int, col: int) -> bool:
    return labels is not None and row < len(labels) and col < len(labels[row])


def _apply_exterior_labels(
    fm: FigureManager, row: int, col: int, config: FacetingConfig, data: pd.DataFrame
) -> None:
    if not (config.exterior_x_label or config.exterior_y_label):
        return

    ax = fm.get_axes(row, col)

    # Get grid dimensions to determine exterior positions
    row_values = _extract_dimension_values(data, config.rows, config.row_order)
    col_values = _extract_dimension_values(data, config.cols, config.col_order)
    n_rows = len(row_values) if config.rows else 1
    n_cols = len(col_values) if config.cols else 1  # noqa: F841

    # Apply exterior x label (bottom row only)
    if config.exterior_x_label and row == n_rows - 1:
        ax.set_xlabel(config.exterior_x_label)

    # Apply exterior y label (leftmost column only)
    if config.exterior_y_label and col == 0:
        ax.set_ylabel(config.exterior_y_label)


def get_grid_dimensions(data: pd.DataFrame, config: FacetingConfig) -> tuple[int, int]:
    assert not data.empty, "Cannot compute dimensions from empty DataFrame"

    # For targeted plotting, we don't need to compute dimensions from data
    # since we'll be placing data at a specific position
    if config.target_row is not None and config.target_col is not None:
        # Return dimensions that will accommodate the target position
        return max(config.target_row + 1, 1), max(config.target_col + 1, 1)

    n_rows = len(data[config.rows].unique()) if config.rows else 1
    n_cols = len(data[config.cols].unique()) if config.cols else 1
    return n_rows, n_cols


def _apply_dimension_titles(
    fm: FigureManager, row: int, col: int, config: FacetingConfig, data: pd.DataFrame
) -> None:
    if not (config.row_titles or config.col_titles):
        return

    ax = fm.get_axes(row, col)

    # Get dimension values using same logic as faceting system
    row_values = _extract_dimension_values(data, config.rows, config.row_order)
    col_values = _extract_dimension_values(data, config.cols, config.col_order)

    # Row titles (left side, first column only)
    if config.row_titles and col == 0 and row < len(row_values):
        title = _resolve_dimension_title(config.row_titles, row, row_values)
        if title:
            _add_row_title(ax, title)

    # Column titles (top, first row only)
    if config.col_titles and row == 0 and col < len(col_values):
        title = _resolve_dimension_title(config.col_titles, col, col_values)
        if title:
            ax.set_title(title, pad=10)


def _resolve_dimension_title(
    title_config: bool | list[str], index: int, dimension_values: list[Any]
) -> str | None:
    if title_config is True:
        return str(dimension_values[index]) if index < len(dimension_values) else None
    elif isinstance(title_config, list):
        return title_config[index] if index < len(title_config) else None
    return None


def _add_row_title(ax: matplotlib.axes.Axes, title: str, offset: float = -0.15) -> None:
    ax_left = ax.twinx()
    ax_left.yaxis.set_label_position("left")
    ax_left.spines["left"].set_position(("axes", offset))
    ax_left.spines["left"].set_visible(False)
    ax_left.set_yticks([])
    ax_left.set_ylabel(
        title,
        rotation=0,
        size="large",
        ha="right",
        va="center",
    )


def _apply_grid_styling(fm: FigureManager, row: int, col: int) -> None:
    ax = fm.get_axes(row, col)
    apply_grid_styling(ax, fm.styler)
