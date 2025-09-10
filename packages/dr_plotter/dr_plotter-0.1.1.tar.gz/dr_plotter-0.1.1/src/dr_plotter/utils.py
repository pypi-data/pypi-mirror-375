from __future__ import annotations

import matplotlib.pyplot as plt


def get_axes_from_grid(
    axes: plt.Axes, row: int | None = None, col: int | None = None
) -> plt.Axes:
    if not hasattr(axes, "__len__"):
        return axes

    if not hasattr(axes, "ndim") and len(axes) > 0:
        first_ax = axes[0]
        assert (
            hasattr(first_ax, "get_gridspec") and first_ax.get_gridspec() is not None
        ), "Cannot determine grid dimensions: first axis has no gridspec"

        gs = first_ax.get_gridspec()
        nrows, ncols = gs.nrows, gs.ncols

        assert row is not None and col is not None, (
            "Must specify both row and col for list-based axes"
        )
        linear_index = row * ncols + col
        assert linear_index < len(axes), (
            f"Index {linear_index} (row={row}, col={col}) "
            f"out of bounds for {len(axes)} axes"
        )
        return axes[linear_index]

    if hasattr(axes, "ndim") and axes.ndim == 1:
        if len(axes) > 1:
            first_ax = axes[0]
            if (
                hasattr(first_ax, "get_gridspec")
                and first_ax.get_gridspec() is not None
            ):
                gs = first_ax.get_gridspec()
                nrows, ncols = gs.nrows, gs.ncols

                if ncols == 1 and nrows > 1:
                    assert row is not None, "Must specify row for vertical grid layout"
                    return axes[row]
                elif nrows == 1 and ncols > 1:
                    assert col is not None, (
                        "Must specify col for horizontal grid layout"
                    )
                    return axes[col]
        idx = col if col is not None else row
        assert idx is not None, "Must specify either row or col for 1D axes array"
        return axes[idx]

    if row is not None and col is not None:
        return axes[row, col]
    elif row is not None:
        return axes[row, :]
    elif col is not None:
        return axes[:, col]

    return axes
